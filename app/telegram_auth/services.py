import hashlib
import hmac
import secrets
import time
from uuid import UUID

from auth.dal import AuthRepo
from auth.errors import InvalidLoginOrPasswordError
from auth.models import Auth
from auth.services import AuthService
from core.settings import settings
from qr_code.dal import QrCodeRepo
from telegram_auth.dal import TelegramLinkCodeRepo, TelegramLinkRepo
from telegram_auth.errors import (
    BotIntegrationDisabledError,
    InvalidLinkCodeError,
    InvalidTelegramWidgetDataError,
    TargetAccountAlreadyLinkedError,
)
from telegram_auth.models import TelegramLink, TelegramLinkCode
from user.dal import UserRepo
from user.models import User

WIDGET_AUTH_MAX_AGE_SECONDS = 600
LINK_CODE_TTL_SECONDS = 600


def verify_widget_data(data: dict[str, str], bot_token: str) -> int:
    received_hash = data.get("hash")
    if not received_hash:
        raise InvalidTelegramWidgetDataError
    fields = {key: value for key, value in data.items() if key != "hash"}
    check_string = "\n".join(f"{key}={fields[key]}" for key in sorted(fields))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise InvalidTelegramWidgetDataError
    try:
        telegram_id = int(data["id"])
        auth_date = int(data["auth_date"])
    except (KeyError, ValueError):
        raise InvalidTelegramWidgetDataError
    if time.time() - auth_date > WIDGET_AUTH_MAX_AGE_SECONDS:
        raise InvalidTelegramWidgetDataError
    return telegram_id


class TelegramAuthService:
    def __init__(
        self,
        link_repo: TelegramLinkRepo,
        link_code_repo: TelegramLinkCodeRepo,
        auth_service: AuthService,
        auth_repo: AuthRepo,
        user_repo: UserRepo,
        qr_code_repo: QrCodeRepo,
    ):
        self._link_repo = link_repo
        self._link_code_repo = link_code_repo
        self._auth_service = auth_service
        self._auth_repo = auth_repo
        self._user_repo = user_repo
        self._qr_code_repo = qr_code_repo

    async def exchange(self, telegram_id: int) -> tuple[str, str]:
        link = await self._link_repo.get_by_telegram_id(telegram_id)
        if link is not None:
            auth = await self._auth_repo.get_by_user_id(link.user_id)
            return await self._auth_service.issue_token_pair(auth)

        username = self._auto_username(telegram_id)
        user = await self._user_repo.create_and_get(User(username=username))
        password = secrets.token_urlsafe(32)
        auth = await self._auth_service.create_auth(user.id, username, password)
        await self._link_repo.create(TelegramLink(telegram_id=telegram_id, user_id=user.id))
        return await self._auth_service.issue_token_pair(auth)

    async def login_via_widget(self, data: dict[str, str]) -> tuple[str, str]:
        if not settings.BOT_TOKEN:
            raise BotIntegrationDisabledError
        telegram_id = verify_widget_data(data, settings.BOT_TOKEN)
        return await self.exchange(telegram_id)

    async def link(self, telegram_id: int, username: str, password: str) -> tuple[str, str]:
        try:
            target_auth = await self._auth_repo.get_by_username(username)
        except Auth.NotFoundError:
            raise InvalidLoginOrPasswordError
        if not self._auth_service.verify_password(password, target_auth.password_hash):
            raise InvalidLoginOrPasswordError

        return await self._link_to_auth(telegram_id, target_auth)

    async def create_link_code(self, user_id: UUID) -> str:
        code = secrets.token_urlsafe(16)
        expires_at = int(time.time()) + LINK_CODE_TTL_SECONDS
        await self._link_code_repo.create(TelegramLinkCode(code=code, user_id=user_id, expires_at=expires_at))
        return code

    async def link_by_code(self, telegram_id: int, code: str) -> tuple[str, str]:
        link_code = await self._link_code_repo.get_by_code(code)
        if link_code is None or link_code.expires_at < time.time():
            raise InvalidLinkCodeError
        await self._link_code_repo.delete_by_code(code)
        try:
            target_auth = await self._auth_repo.get_by_user_id(link_code.user_id)
        except Auth.NotFoundError:
            raise InvalidLinkCodeError
        return await self._link_to_auth(telegram_id, target_auth)

    async def _link_to_auth(self, telegram_id: int, target_auth: Auth) -> tuple[str, str]:
        existing_link_for_target = await self._link_repo.get_by_user_id(target_auth.user_id)
        if existing_link_for_target is not None and existing_link_for_target.telegram_id != telegram_id:
            raise TargetAccountAlreadyLinkedError

        current_link = await self._link_repo.get_by_telegram_id(telegram_id)
        if current_link is None:
            await self._link_repo.create(TelegramLink(telegram_id=telegram_id, user_id=target_auth.user_id))
        elif current_link.user_id != target_auth.user_id:
            await self._qr_code_repo.transfer_owner(current_link.user_id, target_auth.user_id)
            old_user_id = current_link.user_id
            await self._link_repo.update_user_id(telegram_id, target_auth.user_id)
            await self._delete_auto_account(old_user_id)

        return await self._auth_service.issue_token_pair(target_auth)

    async def _delete_auto_account(self, user_id) -> None:
        try:
            auth = await self._auth_repo.get_by_user_id(user_id)
        except Auth.NotFoundError:
            auth = None
        if auth is not None:
            await self._auth_repo.delete(auth.id)
        try:
            await self._user_repo.delete(user_id)
        except User.NotFoundError:
            pass

    @staticmethod
    def _auto_username(telegram_id: int) -> str:
        return f"tg_{telegram_id}"

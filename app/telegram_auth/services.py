import secrets

from auth.dal import AuthRepo
from auth.errors import InvalidLoginOrPasswordError
from auth.models import Auth
from auth.services import AuthService
from qr_code.dal import QrCodeRepo
from telegram_auth.dal import TelegramLinkRepo
from telegram_auth.errors import TargetAccountAlreadyLinkedError
from telegram_auth.models import TelegramLink
from user.dal import UserRepo
from user.models import User


class TelegramAuthService:
    def __init__(
        self,
        link_repo: TelegramLinkRepo,
        auth_service: AuthService,
        auth_repo: AuthRepo,
        user_repo: UserRepo,
        qr_code_repo: QrCodeRepo,
    ):
        self._link_repo = link_repo
        self._auth_service = auth_service
        self._auth_repo = auth_repo
        self._user_repo = user_repo
        self._qr_code_repo = qr_code_repo

    async def exchange(self, telegram_id: int) -> tuple[str, str]:
        link = await self._link_repo.get_by_telegram_id(telegram_id)
        if link is not None:
            auth = await self._auth_repo.get_by_user_id(link.user_id)
            return self._auth_service.create_access_refresh_token_pair(auth)

        username = self._auto_username(telegram_id)
        user = await self._user_repo.create_and_get(User(username=username))
        password = secrets.token_urlsafe(32)
        auth = await self._auth_service.create_auth(user.id, username, password)
        await self._link_repo.create(TelegramLink(telegram_id=telegram_id, user_id=user.id))
        return self._auth_service.create_access_refresh_token_pair(auth)

    async def link(self, telegram_id: int, username: str, password: str) -> tuple[str, str]:
        try:
            target_auth = await self._auth_repo.get_by_username(username)
        except Auth.NotFoundError:
            raise InvalidLoginOrPasswordError
        if not self._auth_service.verify_password(password, target_auth.password_hash):
            raise InvalidLoginOrPasswordError

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

        return self._auth_service.create_access_refresh_token_pair(target_auth)

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

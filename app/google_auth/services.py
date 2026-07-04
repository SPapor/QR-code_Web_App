import secrets
from datetime import timedelta
from urllib.parse import urlencode

import httpx
import jwt

from auth.dal import AuthRepo
from auth.errors import NotAuthorizedError
from auth.services import AuthService
from core.settings import settings
from google_auth.dal import GoogleLinkRepo
from google_auth.errors import GoogleExchangeFailedError, GoogleIntegrationDisabledError, InvalidGoogleStateError
from google_auth.models import GoogleLink
from user.dal import UserRepo
from user.models import User

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")
STATE_TTL = timedelta(minutes=10)


class GoogleAuthService:
    def __init__(
        self,
        link_repo: GoogleLinkRepo,
        auth_service: AuthService,
        auth_repo: AuthRepo,
        user_repo: UserRepo,
    ):
        self._link_repo = link_repo
        self._auth_service = auth_service
        self._auth_repo = auth_repo
        self._user_repo = user_repo

    def build_auth_url(self) -> str:
        self._require_enabled()
        state = self._auth_service.create_jwt_token({"token_type": "google_state"}, STATE_TTL)
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": self._redirect_uri(),
            "response_type": "code",
            "scope": "openid email",
            "state": state,
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    def verify_state(self, state: str | None) -> None:
        if not state:
            raise InvalidGoogleStateError
        try:
            payload = AuthService.decode_jwt_token(state)
        except NotAuthorizedError:
            raise InvalidGoogleStateError
        if payload.get("token_type") != "google_state":
            raise InvalidGoogleStateError

    async def login_with_code(self, code: str) -> tuple[str, str]:
        self._require_enabled()
        claims = await self._fetch_id_token_claims(code)
        google_sub = claims["sub"]
        email = claims.get("email") or f"google_{google_sub}"

        link = await self._link_repo.get_by_sub(google_sub)
        if link is not None:
            auth = await self._auth_repo.get_by_user_id(link.user_id)
            return self._auth_service.create_access_refresh_token_pair(auth)

        username = email
        if await self._user_repo.crud.get_by_username(username) is not None:
            username = f"g_{google_sub}"
        user = await self._user_repo.create_and_get(User(username=username))
        password = secrets.token_urlsafe(32)
        auth = await self._auth_service.create_auth(user.id, username, password)
        await self._link_repo.create(GoogleLink(google_sub=google_sub, user_id=user.id, email=email))
        return self._auth_service.create_access_refresh_token_pair(auth)

    async def _fetch_id_token_claims(self, code: str) -> dict:
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": self._redirect_uri(),
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=data)
        if response.status_code != 200:
            raise GoogleExchangeFailedError
        id_token = response.json().get("id_token")
        if not id_token:
            raise GoogleExchangeFailedError
        # the id_token comes straight from Google's token endpoint over TLS,
        # so its signature is not re-verified against Google's JWKS here
        try:
            claims = jwt.decode(id_token, options={"verify_signature": False})
        except jwt.DecodeError:
            raise GoogleExchangeFailedError
        if claims.get("aud") != settings.GOOGLE_CLIENT_ID or claims.get("iss") not in GOOGLE_ISSUERS:
            raise GoogleExchangeFailedError
        if not claims.get("sub"):
            raise GoogleExchangeFailedError
        return claims

    @staticmethod
    def _require_enabled() -> None:
        if not (settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET):
            raise GoogleIntegrationDisabledError

    @staticmethod
    def _redirect_uri() -> str:
        return f"{settings.API_SCHEME}://{settings.API_URL}/auth/google/callback"

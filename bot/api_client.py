from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx


class BackendError(Exception):
    def __init__(self, status_code: int, detail: str = ""):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class AuthExpiredError(BackendError):
    pass


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


@dataclass
class QrCode:
    id: UUID
    name: str
    link: str


class BackendClient:
    def __init__(self, base_url: str, bot_shared_secret: str):
        self._base_url = base_url.rstrip("/")
        self._bot_secret_headers = {"X-Bot-Secret": bot_shared_secret}
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=10.0)

    async def close(self) -> None:
        await self._client.aclose()

    @property
    def base_url(self) -> str:
        return self._base_url

    def qr_image_url(self, qr_code_id: UUID) -> str:
        return f"{self._base_url}/qr_code/{qr_code_id}/image"

    def qr_redirect_url(self, qr_code_id: UUID) -> str:
        return f"{self._base_url}/qr_code/{qr_code_id}"

    async def tg_exchange(self, telegram_id: int) -> TokenPair:
        resp = await self._client.post(
            "/auth/telegram/exchange",
            json={"telegram_id": telegram_id},
            headers=self._bot_secret_headers,
        )
        return self._token_pair_from_response(resp)

    async def tg_link(self, telegram_id: int, username: str, password: str) -> TokenPair:
        resp = await self._client.post(
            "/auth/telegram/link",
            json={"telegram_id": telegram_id, "username": username, "password": password},
            headers=self._bot_secret_headers,
        )
        return self._token_pair_from_response(resp)

    async def tg_link_by_code(self, telegram_id: int, code: str) -> TokenPair:
        resp = await self._client.post(
            "/auth/telegram/link_by_code",
            json={"telegram_id": telegram_id, "code": code},
            headers=self._bot_secret_headers,
        )
        return self._token_pair_from_response(resp)

    async def refresh(self, refresh_token: str) -> TokenPair:
        resp = await self._client.post(
            "/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )
        if resp.status_code == 401:
            raise AuthExpiredError(401, "refresh token rejected")
        return self._token_pair_from_response(resp)

    async def list_qr_codes(self, access_token: str) -> list[QrCode]:
        data = await self._authed_json("GET", "/qr_code/", access_token)
        return [QrCode(id=UUID(item["id"]), name=item["name"], link=item["link"]) for item in data]

    async def create_qr_code(self, access_token: str, name: str, link: str) -> QrCode:
        data = await self._authed_json(
            "POST", "/qr_code/", access_token, params={"name": name, "link": link}
        )
        return QrCode(id=UUID(data["id"]), name=data["name"], link=data["link"])

    async def update_qr_code(self, access_token: str, qr_code_id: UUID, name: str, link: str) -> QrCode:
        data = await self._authed_json(
            "PUT",
            f"/qr_code/{qr_code_id}",
            access_token,
            params={"name": name, "link": link},
        )
        return QrCode(id=UUID(data["id"]), name=data["name"], link=data["link"])

    async def delete_qr_code(self, access_token: str, qr_code_id: UUID) -> None:
        await self._authed_json("DELETE", f"/qr_code/{qr_code_id}", access_token)

    async def _authed_json(
        self,
        method: str,
        path: str,
        access_token: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        resp = await self._client.request(
            method,
            path,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code == 401:
            raise AuthExpiredError(401, "access token rejected")
        if resp.status_code >= 400:
            raise BackendError(resp.status_code, _safe_detail(resp))
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    @staticmethod
    def _token_pair_from_response(resp: httpx.Response) -> TokenPair:
        if resp.status_code >= 400:
            raise BackendError(resp.status_code, _safe_detail(resp))
        body = resp.json()
        access_token = body["access_token"]
        refresh_token = resp.cookies.get("refresh_token")
        if not refresh_token:
            raise BackendError(500, "backend did not set refresh_token cookie")
        return TokenPair(access_token=access_token, refresh_token=refresh_token)


def _safe_detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:200]
    if isinstance(body, dict) and "detail" in body:
        detail = body["detail"]
        if isinstance(detail, str):
            return detail
        return str(detail)
    return str(body)[:200]

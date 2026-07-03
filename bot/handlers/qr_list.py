from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from api_client import BackendClient, BackendError
from auth_session import AuthSession, NotLoggedInError
from keyboards import qr_actions

router = Router(name="qr_list")


@router.message(Command("list"))
async def cmd_list(message: Message, auth: AuthSession, client: BackendClient) -> None:
    try:
        qr_codes = await auth.call(lambda token: client.list_qr_codes(token))
    except NotLoggedInError:
        await message.answer("Please /start first.")
        return
    except BackendError as exc:
        await message.answer(f"Backend error: {exc.detail or exc.status_code}")
        return

    if not qr_codes:
        await message.answer("You don't have any QR codes yet. /new to create one.")
        return

    await message.answer(f"You have {len(qr_codes)} QR code(s):")
    for qr in qr_codes:
        await message.answer(
            f"<b>{_escape(qr.name)}</b>\n{_escape(qr.link)}",
            parse_mode="HTML",
            reply_markup=qr_actions(qr.id),
        )


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

from __future__ import annotations

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, URLInputFile

from api_client import BackendClient, BackendError
from auth_session import AuthSession, NotLoggedInError
from keyboards import confirm_delete

router = Router(name="qr_delete")


@router.callback_query(F.data.startswith("qr:del:"))
async def delete_ask(callback: CallbackQuery, auth: AuthSession) -> None:
    if not await auth.is_logged_in():
        await callback.answer("Please /start first.", show_alert=True)
        return
    qr_code_id = _parse_id(callback.data, 2)
    if qr_code_id is None:
        await callback.answer("Bad callback.")
        return
    await callback.message.answer(
        "Delete this QR code? This cannot be undone.",
        reply_markup=confirm_delete(qr_code_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qr:delok:"))
async def delete_confirm(
    callback: CallbackQuery,
    auth: AuthSession,
    client: BackendClient,
) -> None:
    qr_code_id = _parse_id(callback.data, 2)
    if qr_code_id is None:
        await callback.answer("Bad callback.")
        return
    try:
        await auth.call(lambda token: client.delete_qr_code(token, qr_code_id))
    except NotLoggedInError:
        await callback.answer("Please /start first.", show_alert=True)
        return
    except BackendError as exc:
        await callback.answer(f"Failed: {exc.detail or exc.status_code}", show_alert=True)
        return
    await callback.message.edit_text("Deleted.")
    await callback.answer()


@router.callback_query(F.data == "qr:delno")
async def delete_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Cancelled.")
    await callback.answer()


@router.callback_query(F.data.startswith("qr:png:"))
async def send_png(callback: CallbackQuery, client: BackendClient) -> None:
    qr_code_id = _parse_id(callback.data, 2)
    if qr_code_id is None:
        await callback.answer("Bad callback.")
        return
    await callback.message.answer_photo(
        URLInputFile(client.qr_image_url(qr_code_id), filename=f"{qr_code_id}.png")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qr:url:"))
async def send_url(callback: CallbackQuery, client: BackendClient) -> None:
    qr_code_id = _parse_id(callback.data, 2)
    if qr_code_id is None:
        await callback.answer("Bad callback.")
        return
    await callback.message.answer(client.qr_redirect_url(qr_code_id))
    await callback.answer()


def _parse_id(data: str | None, index: int) -> UUID | None:
    if not data:
        return None
    parts = data.split(":")
    if len(parts) <= index:
        return None
    try:
        return UUID(parts[index])
    except ValueError:
        return None

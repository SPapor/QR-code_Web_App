from __future__ import annotations

from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api_client import BackendClient, BackendError
from auth_session import AuthSession, NotLoggedInError

router = Router(name="qr_edit")


class EditStates(StatesGroup):
    waiting_name = State()
    waiting_link = State()


@router.callback_query(F.data.startswith("qr:edit:"))
async def edit_start(callback: CallbackQuery, state: FSMContext, auth: AuthSession) -> None:
    if not await auth.is_logged_in():
        await callback.answer("Please /start first.", show_alert=True)
        return
    qr_code_id = _parse_id(callback.data)
    if qr_code_id is None:
        await callback.answer("Bad callback.")
        return
    await state.set_state(EditStates.waiting_name)
    await state.update_data(qr_code_id=str(qr_code_id))
    await callback.message.answer("New name?")
    await callback.answer()


@router.message(EditStates.waiting_name, F.text)
async def edit_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(EditStates.waiting_link)
    await message.answer("New URL?")


@router.message(EditStates.waiting_link, F.text)
async def edit_link(
    message: Message,
    state: FSMContext,
    auth: AuthSession,
    client: BackendClient,
) -> None:
    data = await state.get_data()
    qr_code_id = UUID(data["qr_code_id"])
    name = data.get("name", "")
    link = message.text.strip()
    await state.clear()

    try:
        qr = await auth.call(lambda token: client.update_qr_code(token, qr_code_id, name, link))
    except NotLoggedInError:
        await message.answer("Session expired. Please /start again.")
        return
    except BackendError as exc:
        await message.answer(f"Failed to update: {exc.detail or exc.status_code}")
        return

    await message.answer(f"Updated:\n<b>{_escape(qr.name)}</b>\n{_escape(qr.link)}", parse_mode="HTML")


def _parse_id(data: str | None) -> UUID | None:
    if not data:
        return None
    parts = data.split(":")
    if len(parts) != 3:
        return None
    try:
        return UUID(parts[2])
    except ValueError:
        return None


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

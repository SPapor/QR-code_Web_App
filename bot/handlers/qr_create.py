from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, URLInputFile

from api_client import BackendClient, BackendError
from auth_session import AuthSession, NotLoggedInError
from keyboards import qr_actions

router = Router(name="qr_create")


class CreateStates(StatesGroup):
    waiting_name = State()
    waiting_link = State()


@router.message(Command("new"))
async def cmd_new(message: Message, auth: AuthSession, state: FSMContext) -> None:
    if not await auth.is_logged_in():
        await message.answer("Please /start first.")
        return
    await state.set_state(CreateStates.waiting_name)
    await message.answer("Name for the QR code?")


@router.message(CreateStates.waiting_name, F.text)
async def create_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(CreateStates.waiting_link)
    await message.answer("Destination URL?")


@router.message(CreateStates.waiting_link, F.text)
async def create_link(
    message: Message,
    state: FSMContext,
    auth: AuthSession,
    client: BackendClient,
) -> None:
    data = await state.get_data()
    name = data.get("name", "")
    link = message.text.strip()
    await state.clear()

    try:
        qr = await auth.call(lambda token: client.create_qr_code(token, name, link))
    except NotLoggedInError:
        await message.answer("Session expired. Please /start again.")
        return
    except BackendError as exc:
        await message.answer(f"Failed to create: {exc.detail or exc.status_code}")
        return

    await message.answer_photo(
        URLInputFile(client.qr_image_url(qr.id), filename=f"{qr.name}.png"),
        caption=f"<b>{_escape(qr.name)}</b>\n{_escape(qr.link)}",
        parse_mode="HTML",
        reply_markup=qr_actions(qr.id),
    )


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from api_client import BackendClient, BackendError
from auth_session import AuthSession

router = Router(name="auth")


class LinkStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()


HELP_TEXT = (
    "QR-menu bot.\n\n"
    "Commands:\n"
    "/start — sign in (your Telegram account is your identity here)\n"
    "/link — bind to an existing website account (login + password)\n"
    "/logout — forget tokens on this device\n"
    "/list — show your QR codes\n"
    "/new — create a new QR code\n"
    "/cancel — abort the current operation"
)


# must be registered before the plain /start handler, which matches any payload
@router.message(CommandStart(deep_link=True, magic=F.args.startswith("link_")))
async def cmd_start_link(
    message: Message, command: CommandObject, auth: AuthSession, client: BackendClient
) -> None:
    if message.from_user is None:
        await message.answer("Cannot identify Telegram user.")
        return
    code = (command.args or "")[len("link_"):]
    try:
        pair = await client.tg_link_by_code(message.from_user.id, code)
    except BackendError as exc:
        await message.answer(f"Link failed: {exc.detail or exc.status_code}")
        return
    await auth.store_tokens(pair)
    await message.answer(
        "Linked! This chat is now bound to your website account.\n"
        "Use /list to see your QR codes or /new to create one."
    )


@router.message(CommandStart())
async def cmd_start(message: Message, auth: AuthSession, client: BackendClient) -> None:
    if await auth.is_logged_in():
        await message.answer("You are signed in. " + HELP_TEXT)
        return
    if message.from_user is None:
        await message.answer("Cannot identify Telegram user.")
        return
    try:
        pair = await client.tg_exchange(message.from_user.id)
    except BackendError as exc:
        await message.answer(f"Sign-in failed: {exc.detail or exc.status_code}")
        return
    await auth.store_tokens(pair)
    await message.answer(
        "Welcome! Your QR codes are stored under your Telegram identity.\n\n"
        "Use /new to create a code, /list to see all of them, "
        "or /link to bind this chat to an existing website account."
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    await state.clear()
    if current is None:
        await message.answer("Nothing to cancel.")
    else:
        await message.answer("Cancelled.")


@router.message(Command("logout"))
async def cmd_logout(message: Message, auth: AuthSession, state: FSMContext) -> None:
    await state.clear()
    if await auth.is_logged_in():
        await auth.clear()
        await message.answer("Signed out on this device. /start to sign in again.")
    else:
        await message.answer("You weren't signed in.")


@router.message(Command("link"))
async def cmd_link(message: Message, auth: AuthSession, state: FSMContext) -> None:
    if not await auth.is_logged_in():
        await message.answer("Please /start first.")
        return
    await state.set_state(LinkStates.waiting_username)
    await message.answer(
        "Linking to an existing website account.\n"
        "Any QR codes already created in this bot will be moved to the linked account.\n\n"
        "Website username?"
    )


@router.message(LinkStates.waiting_username, F.text)
async def link_username(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.text.strip())
    await state.set_state(LinkStates.waiting_password)
    await message.answer("Password? (I will delete the message after reading it.)")


@router.message(LinkStates.waiting_password, F.text)
async def link_password(
    message: Message,
    state: FSMContext,
    auth: AuthSession,
    client: BackendClient,
) -> None:
    data = await state.get_data()
    username = data.get("username", "")
    password = message.text
    await _try_delete(message)
    await state.clear()

    if message.from_user is None:
        await message.answer("Cannot identify Telegram user.")
        return
    try:
        pair = await client.tg_link(message.from_user.id, username, password)
    except BackendError as exc:
        await message.answer(f"Link failed: {exc.detail or exc.status_code}")
        return
    await auth.store_tokens(pair)
    await message.answer("Linked. This chat now controls your website account.")


async def _try_delete(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass

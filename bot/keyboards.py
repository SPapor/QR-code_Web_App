from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

BTN_LIST = "📋 My QR codes"
BTN_NEW = "➕ New QR"
BTN_HELP = "❓ Help"
BTN_CANCEL = "✖️ Cancel"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_LIST), KeyboardButton(text=BTN_NEW)],
            [KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
    )


def qr_actions(qr_code_id: UUID) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🖼 PNG", callback_data=f"qr:png:{qr_code_id}"),
                InlineKeyboardButton(text="🔗 Link", callback_data=f"qr:url:{qr_code_id}"),
            ],
            [
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"qr:edit:{qr_code_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"qr:del:{qr_code_id}"),
            ],
        ]
    )


def confirm_delete(qr_code_id: UUID) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Yes, delete", callback_data=f"qr:delok:{qr_code_id}"),
                InlineKeyboardButton(text="Cancel", callback_data="qr:delno"),
            ],
        ]
    )

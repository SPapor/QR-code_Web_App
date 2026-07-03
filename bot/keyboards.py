from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

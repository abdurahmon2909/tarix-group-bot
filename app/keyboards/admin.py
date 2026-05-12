from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def admin_panel_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Guruhlar",
                    callback_data="groups_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Report",
                    callback_data="reports_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Broadcast",
                    callback_data="broadcast_menu",
                )
            ],
        ]
    )
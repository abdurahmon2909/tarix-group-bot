from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def admin_main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Reports",
                    callback_data="reports_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📂 Guruhlar",
                    callback_data="groups_menu",
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
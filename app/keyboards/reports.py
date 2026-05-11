from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def reports_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 2 soat",
                    callback_data="report:2",
                ),
                InlineKeyboardButton(
                    text="📊 4 soat",
                    callback_data="report:4",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 8 soat",
                    callback_data="report:8",
                ),
                InlineKeyboardButton(
                    text="📊 1 kun",
                    callback_data="report:24",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 3 kun",
                    callback_data="report:72",
                ),
                InlineKeyboardButton(
                    text="📊 1 hafta",
                    callback_data="report:168",
                ),
            ],
        ]
    )
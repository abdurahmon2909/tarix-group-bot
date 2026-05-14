from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.config import settings


def subscription_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📢 Kanalga o'tish",
                    url=settings.CHANNEL_LINK,
                ),
            ],

            [
                InlineKeyboardButton(
                    text="✅ Tekshirish",
                    callback_data="check_subscription",
                ),
            ],
        ]
    )
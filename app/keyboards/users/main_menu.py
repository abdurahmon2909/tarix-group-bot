from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def user_main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✏️ Ismni o‘zgartirish",
                    callback_data="change_name",
                ),

                InlineKeyboardButton(
                    text="📄 Test tekshirish",
                    callback_data="check_test",
                ),
            ],

            [
                InlineKeyboardButton(
                    text="📨 Ustozga yozish",
                    callback_data="support",
                ),

                InlineKeyboardButton(
                    text="👤 Profilim",
                    callback_data="profile",
                ),
            ],

            [
                InlineKeyboardButton(
                    text=(
                        "👤 Fazliddin Burxonov "
                        "(shaxsiy)"
                    ),
                    url="https://t.me/Fazliddin_Burxonov",
                ),
            ],
        ]
    )
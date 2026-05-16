from __future__ import annotations

import asyncio

from aiogram import Bot

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.database.repositories.users import (
    get_all_users,
)

from app.config import settings


# =========================
# CHECK USER SUBSCRIPTION
# =========================

async def check_user_subscription(
    bot: Bot,
    user_id: int,
) -> bool:

    channels = (
        settings.REQUIRED_CHANNELS
    )

    for channel_id in channels:

        try:

            member = (
                await bot.get_chat_member(
                    chat_id=channel_id,
                    user_id=user_id,
                )
            )

            if member.status in (
                "left",
                "kicked",
            ):
                return False

        except:

            return False

    return True


# =========================
# LOOP
# =========================

async def subscription_checker_loop(
    bot: Bot,
):

    while True:

        users = await get_all_users()

        channels = (
            settings.REQUIRED_CHANNELS
        )

        for user in users:

            try:

                subscribed = (
                    await check_user_subscription(
                        bot=bot,
                        user_id=(
                            user.telegram_id
                        ),
                    )
                )

                if subscribed:
                    continue

                keyboard = []

                for channel_id in channels:

                    try:

                        invite_link = (
                            await bot.export_chat_invite_link(
                                channel_id
                            )
                        )

                    except:

                        invite_link = None

                    if invite_link:

                        keyboard.append([
                            InlineKeyboardButton(
                                text=(
                                    "📢 Kanalga "
                                    "obuna bo‘lish"
                                ),
                                url=invite_link,
                            )
                        ])

                keyboard.append([
                    InlineKeyboardButton(
                        text="✅ Tekshirish",
                        callback_data=(
                            "recheck_subscription"
                        ),
                    )
                ])

                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=(
                        "⚠️ Botdan foydalanish "
                        "uchun kanalga qayta "
                        "obuna bo‘ling"
                    ),
                    reply_markup=(
                        InlineKeyboardMarkup(
                            inline_keyboard=keyboard
                        )
                    ),
                )

                await asyncio.sleep(0.2)

            except:
                pass

        await asyncio.sleep(
            60 * 60
        )
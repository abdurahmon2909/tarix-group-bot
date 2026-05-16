from __future__ import annotations

from aiogram import Bot

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.config import settings

from app.database.repositories.users import (
    get_all_users,
)

from app.database.repositories.channels import (
    get_required_channels,
)


async def check_user_subscription(
    bot: Bot,
    user_id: int,
) -> bool:

    channels = (
        await get_required_channels()
    )

    for channel in channels:

        try:

            member = (
                await bot.get_chat_member(
                    chat_id=channel.telegram_chat_id,
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


async def subscription_checker_loop(
    bot: Bot,
):

    while True:

        users = await get_all_users()

        for user in users:

            try:

                subscribed = (
                    await check_user_subscription(
                        bot=bot,
                        user_id=user.telegram_id,
                    )
                )

                if subscribed:
                    continue

                channels = (
                    await get_required_channels()
                )

                keyboard = []

                for channel in channels:

                    keyboard.append([
                        InlineKeyboardButton(
                            text=(
                                f"📢 "
                                f"{channel.title}"
                            ),
                            url=channel.invite_link,
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
                        "uchun qayta obuna "
                        "bo‘ling"
                    ),
                    reply_markup=(
                        InlineKeyboardMarkup(
                            inline_keyboard=keyboard
                        )
                    ),
                )

            except:
                pass

        import asyncio

        await asyncio.sleep(
            60 * 60
        )
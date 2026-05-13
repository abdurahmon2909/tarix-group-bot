from __future__ import annotations

from aiogram import (
    Router,
)
from aiogram.enums import (
    ChatType,
)
from aiogram.types import (
    Message,
)

from app.database.repositories.groups import (
    create_group_if_not_exists,
    is_group_active,
)

from app.database.repositories.messages import (
    save_group_message,
)

router = Router()


@router.message()
async def track_group_messages(
    message: Message,
):

    print("TRACKER HIT")

    if message.chat.type not in [
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ]:
        return

    if not message.from_user:
        return

    print(
        "GROUP MESSAGE:",
        message.text,
    )
    # =========================
    # AUTO DELETE JOIN/LEFT
    # =========================

    try:

        if message.new_chat_members:

            is_bot_join = any(
                user.is_bot
                and user.id == message.bot.id
                for user in message.new_chat_members
            )

            if not is_bot_join:
                await message.delete()

                print(
                    "JOIN MESSAGE DELETED"
                )

                return

        if message.left_chat_member:

            is_bot_leave = (
                    message.left_chat_member.is_bot
                    and (
                            message.left_chat_member.id
                            == message.bot.id
                    )
            )

            if not is_bot_leave:
                await message.delete()

                print(
                    "LEFT MESSAGE DELETED"
                )

                return

    except Exception as e:

        print(
            "JOIN/LEFT DELETE ERROR:",
            repr(e),
        )
    # =========================
    # AUTO CREATE GROUP
    # =========================

    await create_group_if_not_exists(
        telegram_chat_id=message.chat.id,
        title=message.chat.title or "Noma'lum",
    )

    # =========================
    # CHECK ACTIVE
    # =========================

    active = await is_group_active(
        message.chat.id
    )

    print(
        "GROUP ACTIVE:",
        active,
    )

    if not active:
        return

    # =========================
    # SAVE MESSAGE
    # =========================

    try:

        await save_group_message(
            chat_id=message.chat.id,
            telegram_message_id=(
                message.message_id
            ),
            telegram_user_id=(
                message.from_user.id
            ),
            full_name=(
                message.from_user.full_name
            ),
            username=(
                message.from_user.username
            ),
            text=message.text or "",
            sent_at=message.date.replace(
                tzinfo=None
            ),
        )

        print(
            "MESSAGE SAVED"
        )

    except Exception as e:

        print(
            "SAVE ERROR:",
            repr(e),
        )
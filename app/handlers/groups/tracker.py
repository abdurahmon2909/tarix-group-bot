from __future__ import annotations

from aiogram import Router

from aiogram.types import (
    Message,
)

from app.database.repositories.groups import (
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
        "group",
        "supergroup",
    ]:
        return

    print(
        "GROUP MESSAGE:",
        message.text,
    )

    active = await is_group_active(
        message.chat.id
    )

    print(
        "GROUP ACTIVE:",
        active,
    )

    if not active:
        return

    if not message.from_user:
        return

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
            e,
        )
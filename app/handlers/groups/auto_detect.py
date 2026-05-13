from __future__ import annotations

from aiogram import (
    Router,
)

from aiogram.types import (
    Message,
)

from app.database.repositories.groups import (
    create_group_if_not_exists,
)

router = Router()


@router.message(
    lambda message: (
        message.chat.type
        in ["group", "supergroup"]
    )
)
async def detect_new_group(
    message: Message,
):

    print("AUTO DETECT HIT")

    print(
        "NEW GROUP:",
        message.chat.title,
    )

    await create_group_if_not_exists(
        telegram_chat_id=message.chat.id,
        title=message.chat.title or "Noma'lum",
    )
from __future__ import annotations

from aiogram import Router
from aiogram.types import (
    Message,
)

from app.database.repositories.groups import (
    create_group_if_not_exists,
)

router = Router()


@router.message()
async def detect_new_group(
    message: Message,
):

    if message.chat.type not in [
        "group",
        "supergroup",
    ]:
        return

    await create_group_if_not_exists(
        telegram_chat_id=message.chat.id,
        title=message.chat.title or "Noma'lum",
    )
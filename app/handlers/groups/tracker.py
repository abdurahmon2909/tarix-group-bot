from __future__ import annotations

from aiogram import Router
from aiogram.types import Message

from app.services.groups.cache import (
    is_group_active,
)

from app.services.messages.message_service import (
    save_group_message,
)

router = Router()


@router.message()
async def track_group_messages(
    message: Message,
):

    if message.chat.type not in [
        "group",
        "supergroup",
    ]:
        return

    if not is_group_active(
        message.chat.id
    ):
        return

    if not message.from_user:
        return

    await save_group_message(
        chat_id=message.chat.id,
        telegram_message_id=message.message_id,
        telegram_user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        text=message.text,
        sent_at=message.date,
    )
from __future__ import annotations

from aiogram import Router
from aiogram.types import ChatMemberUpdated

from app.services.groups.group_service import (
    auto_register_group,
)

router = Router()


@router.my_chat_member()
async def bot_added_to_group(
    event: ChatMemberUpdated,
):

    chat = event.chat

    if chat.type not in [
        "group",
        "supergroup",
    ]:
        return

    await auto_register_group(
        telegram_chat_id=chat.id,
        title=chat.title or "Noma'lum guruh",
        username=chat.username,
    )
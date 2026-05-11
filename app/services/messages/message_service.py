from __future__ import annotations

from datetime import datetime

from app.database.repositories.messages import (
    create_message,
)


async def save_group_message(
    chat_id: int,
    telegram_message_id: int,
    telegram_user_id: int,
    full_name: str,
    username: str | None,
    text: str | None,
    sent_at: datetime,
):

    return await create_message(
        chat_id=chat_id,
        telegram_message_id=telegram_message_id,
        telegram_user_id=telegram_user_id,
        full_name=full_name,
        username=username,
        text=text,
        sent_at=sent_at,
    )
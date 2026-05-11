from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    select,
    func,
)

from app.database.db import async_session
from app.database.models.message import Message


async def create_message(
    chat_id: int,
    telegram_message_id: int,
    telegram_user_id: int,
    full_name: str,
    username: str | None,
    text: str | None,
    sent_at: datetime,
) -> Message:

    async with async_session() as session:

        message = Message(
            chat_id=chat_id,
            telegram_message_id=telegram_message_id,
            telegram_user_id=telegram_user_id,
            full_name=full_name,
            username=username,
            text=text,
            sent_at=sent_at,
        )

        session.add(message)

        await session.commit()

        await session.refresh(message)

        return message


async def get_messages_between(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
) -> list[Message]:

    async with async_session() as session:

        result = await session.execute(
            select(Message).where(
                Message.chat_id == chat_id,
                Message.sent_at >= start_dt,
                Message.sent_at <= end_dt,
            )
        )

        return list(result.scalars().all())


async def get_total_message_count(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
) -> int:

    async with async_session() as session:

        result = await session.execute(
            select(func.count(Message.id)).where(
                Message.chat_id == chat_id,
                Message.sent_at >= start_dt,
                Message.sent_at <= end_dt,
            )
        )

        return result.scalar() or 0
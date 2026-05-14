from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    select,
)
from sqlalchemy import func
from app.database.db import (
    async_session,
)

from app.database.models.message import (
    Message,
)


# =========================
# SAVE MESSAGE
# =========================

async def save_group_message(
    chat_id: int,
    telegram_message_id: int,
    telegram_user_id: int,
    full_name: str,
    username: str | None,
    text: str,
    sent_at: datetime,
):

    async with async_session() as session:

        message = Message(
            chat_id=chat_id,
            telegram_message_id=(
                telegram_message_id
            ),
            telegram_user_id=(
                telegram_user_id
            ),
            full_name=full_name,
            username=username,
            text=text,
            sent_at=sent_at,
        )

        session.add(message)

        await session.commit()


# =========================
# GET MESSAGES RANGE
# =========================

async def get_messages_in_range(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
):

    async with async_session() as session:

        result = await session.execute(
            select(Message).where(
                Message.chat_id == chat_id,
                Message.sent_at >= start_dt,
                Message.sent_at <= end_dt,
            )
        )

        return result.scalars().all()

# =========================
# USER TOTAL MESSAGES
# =========================

async def get_user_total_messages(
    telegram_user_id: int,
) -> int:

    async with async_session() as session:

        result = await session.execute(
            select(
                func.count(Message.id)
            ).where(
                Message.telegram_user_id
                == telegram_user_id
            )
        )

        return result.scalar() or 0


# =========================
# ALL TOTAL MESSAGES
# =========================

async def get_all_total_messages() -> int:

    async with async_session() as session:

        result = await session.execute(
            select(
                func.count(Message.id)
            )
        )

        return result.scalar() or 0
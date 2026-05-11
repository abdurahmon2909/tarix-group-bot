from __future__ import annotations

from sqlalchemy import select

from app.database.db import async_session

from app.database.models.support_message import (
    SupportMessage,
)


async def create_support_mapping(
    forwarded_message_id: int,
    user_id: int,
):

    async with async_session() as session:

        obj = SupportMessage(
            forwarded_message_id=(
                forwarded_message_id
            ),
            user_id=user_id,
        )

        session.add(obj)

        await session.commit()


async def get_user_id_by_forwarded_message(
    forwarded_message_id: int,
) -> int | None:

    async with async_session() as session:

        result = await session.execute(
            select(
                SupportMessage.user_id
            ).where(
                SupportMessage.forwarded_message_id
                == forwarded_message_id
            )
        )

        return result.scalar_one_or_none()
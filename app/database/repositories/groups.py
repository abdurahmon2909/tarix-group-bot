from __future__ import annotations

from sqlalchemy import (
    select,
)

from app.database.db import (
    async_session,
)

from app.database.models.group import (
    Group,
)


# =========================
# CREATE GROUP
# =========================

async def create_group_if_not_exists(
    telegram_chat_id: int,
    title: str,
):

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.telegram_chat_id
                == telegram_chat_id
            )
        )

        group = result.scalar_one_or_none()

        if group:
            return

        new_group = Group(
            telegram_chat_id=telegram_chat_id,
            title=title,
            is_active=False,
        )

        session.add(new_group)

        await session.commit()


# =========================
# GET ACTIVE GROUPS
# =========================

async def get_active_groups():

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.is_active == True
            )
        )

        return result.scalars().all()


# =========================
# GET ACTIVE GROUP IDS
# =========================

async def get_active_group_ids():

    groups = await get_active_groups()

    return [
        group.telegram_chat_id
        for group in groups
    ]


# =========================
# ACTIVATE GROUP
# =========================

async def activate_group(
    telegram_chat_id: int,
):

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.telegram_chat_id
                == telegram_chat_id
            )
        )

        group = result.scalar_one_or_none()

        if not group:
            return False

        group.is_active = True

        await session.commit()

        return True


# =========================
# IS GROUP ACTIVE
# =========================

async def is_group_active(
    telegram_chat_id: int,
) -> bool:

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.telegram_chat_id
                == telegram_chat_id
            )
        )

        group = result.scalar_one_or_none()

        if not group:
            return False

        return group.is_active

# =========================
# PENDING GROUPS
# =========================

async def get_pending_groups():

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.is_active == False
            )
        )

        return result.scalars().all()
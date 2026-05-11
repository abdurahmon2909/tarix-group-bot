from __future__ import annotations

from sqlalchemy import select

from app.database.db import async_session
from app.database.models.group import Group


async def get_group_by_chat_id(
    chat_id: int,
) -> Group | None:

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.telegram_chat_id == chat_id
            )
        )

        return result.scalar_one_or_none()


async def create_group(
    telegram_chat_id: int,
    title: str,
    username: str | None = None,
    is_active: bool = False,
) -> Group:

    async with async_session() as session:

        group = Group(
            telegram_chat_id=telegram_chat_id,
            title=title,
            username=username,
            is_active=is_active,
        )

        session.add(group)

        await session.commit()

        await session.refresh(group)

        return group


async def get_pending_groups() -> list[Group]:

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.is_active == False
            )
        )

        return list(result.scalars().all())


async def activate_group(
    group_id: int,
) -> None:

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.id == group_id
            )
        )

        group = result.scalar_one_or_none()

        if not group:
            return

        group.is_active = True

        await session.commit()


async def get_active_groups() -> list[Group]:

    async with async_session() as session:

        result = await session.execute(
            select(Group).where(
                Group.is_active == True
            )
        )

        return list(result.scalars().all())

async def get_active_group_ids():

    async with async_session() as session:

        result = await session.execute(
            select(Group.telegram_chat_id).where(
                Group.is_active == True
            )
        )

        return list(result.scalars().all())

async def get_group_title(
    chat_id: int,
) -> str:

    async with async_session() as session:

        result = await session.execute(
            select(Group.title).where(
                Group.telegram_chat_id == chat_id
            )
        )

        title = result.scalar_one_or_none()

        return title or "Noma'lum guruh"

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
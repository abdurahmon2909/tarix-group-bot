from __future__ import annotations

from sqlalchemy import select

from app.database.db import async_session
from app.database.models.user import User


async def get_user_by_telegram_id(
    telegram_id: int,
) -> User | None:

    async with async_session() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()


async def create_user(
    telegram_id: int,
    full_name: str,
    username: str | None = None,
) -> User:

    async with async_session() as session:

        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
        )

        session.add(user)

        await session.commit()

        await session.refresh(user)

        return user


async def update_user_fullname(
    telegram_id: int,
    full_name: str,
) -> None:

    async with async_session() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return

        user.full_name = full_name

        await session.commit()


async def upsert_user(
    telegram_id: int,
    full_name: str,
    username: str | None = None,
) -> User:

    existing_user = await get_user_by_telegram_id(
        telegram_id
    )

    if existing_user:

        async with async_session() as session:

            result = await session.execute(
                select(User).where(
                    User.telegram_id == telegram_id
                )
            )

            user = result.scalar_one()

            user.full_name = full_name

            user.username = username

            await session.commit()

            return user

    return await create_user(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
    )
async def get_all_users():

    async with async_session() as session:

        result = await session.execute(
            select(User)
        )

        return list(
            result.scalars().all()
        )
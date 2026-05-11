from __future__ import annotations

from app.database.repositories.users import (
    upsert_user,
    update_user_fullname,
    get_user_by_telegram_id,
)


async def save_user(
    telegram_id: int,
    full_name: str,
    username: str | None = None,
):

    return await upsert_user(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
    )


async def set_user_fullname(
    telegram_id: int,
    full_name: str,
):

    await update_user_fullname(
        telegram_id=telegram_id,
        full_name=full_name,
    )


async def user_has_fullname(
    telegram_id: int,
) -> bool:

    user = await get_user_by_telegram_id(
        telegram_id
    )

    if not user:
        return False

    return bool(user.full_name.strip())
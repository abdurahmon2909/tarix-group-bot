from __future__ import annotations

from app.database.repositories.groups import (
    create_group,
    get_group_by_chat_id,
    get_pending_groups,
    activate_group,
)


async def auto_register_group(
    telegram_chat_id: int,
    title: str,
    username: str | None = None,
):

    existing = await get_group_by_chat_id(
        telegram_chat_id
    )

    if existing:
        return existing

    return await create_group(
        telegram_chat_id=telegram_chat_id,
        title=title,
        username=username,
        is_active=False,
    )


async def get_not_approved_groups():

    return await get_pending_groups()


async def approve_group(
    group_id: int,
):

    await activate_group(group_id)
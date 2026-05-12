from __future__ import annotations

from app.database.repositories.groups import (
    create_group_if_not_exists,
    get_pending_groups,
    activate_group_by_id,
)


async def auto_register_group(
    telegram_chat_id: int,
    title: str,
    username: str | None = None,
):

    await create_group_if_not_exists(
        telegram_chat_id=telegram_chat_id,
        title=title,
    )


async def get_not_approved_groups():

    return await get_pending_groups()


async def approve_group(
    group_id: int,
):

    await activate_group_by_id(
        group_id
    )
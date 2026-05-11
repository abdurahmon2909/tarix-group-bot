from __future__ import annotations

from app.database.repositories.groups import (
    get_active_group_ids,
)

ACTIVE_GROUPS_CACHE = set()


async def refresh_groups_cache():

    global ACTIVE_GROUPS_CACHE

    groups = await get_active_group_ids()

    ACTIVE_GROUPS_CACHE = set(groups)


def is_group_active(
    chat_id: int,
) -> bool:

    return chat_id in ACTIVE_GROUPS_CACHE
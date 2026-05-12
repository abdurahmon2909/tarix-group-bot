from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)

from collections import Counter

from app.database.repositories.messages import (
    get_messages_in_range,
)


async def build_stats(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
    group_name: str = "Guruh",
):

    messages = await get_messages_in_range(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    total_messages = len(messages)

    counter = Counter()

    user_names = {}

    for msg in messages:

        counter[msg.telegram_user_id] += 1

        user_names[msg.telegram_user_id] = (
            msg.full_name
            or "Ism kiritilmagan"
        )

    users = []

    for user_id, msg_count in (
        counter.most_common()
    ):

        share_percent = round(
            (
                msg_count
                / total_messages
                * 100
            ),
            2,
        ) if total_messages else 0

        users.append({
            "telegram_user_id": user_id,
            "full_name": user_names[
                user_id
            ],
            "msg_count": msg_count,
            "share_percent": (
                share_percent
            ),
        })

    return {
        "group_name": group_name,
        "group_id": chat_id,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "total_messages": total_messages,
        "users": users,
    }


async def get_stats_for_hours(
    chat_id: int,
    hours: int,
    group_name: str = "Guruh",
):

    end_dt = datetime.utcnow()

    start_dt = end_dt - timedelta(
        hours=hours
    )

    return await build_stats(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
        group_name=group_name,
    )


async def get_stats_for_range(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
    group_name: str = "Guruh",
):

    return await build_stats(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
        group_name=group_name,
    )
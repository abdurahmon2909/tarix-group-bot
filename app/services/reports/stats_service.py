from __future__ import annotations

from collections import defaultdict

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.database.repositories.messages import (
    get_messages_between,
)


def classify_activity(
    percent: float,
) -> str:

    if percent >= 3:
        return "Faol"

    if percent >= 1:
        return "Yaxshi"

    return "O'rtacha"


async def build_stats(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
):

    messages = await get_messages_between(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    total_messages = len(messages)

    users_map = defaultdict(int)

    names_map = {}

    for msg in messages:

        users_map[
            msg.telegram_user_id
        ] += 1

        names_map[
            msg.telegram_user_id
        ] = msg.full_name

    users = []

    for user_id, count in users_map.items():

        share_percent = round(
            (count / total_messages) * 100,
            2
        ) if total_messages else 0

        users.append({
            "telegram_user_id": user_id,
            "full_name": names_map.get(
                user_id,
                "Ism kiritilmagan",
            ),
            "msg_count": count,
            "share_percent": share_percent,
            "category": classify_activity(
                share_percent
            ),
        })

    users.sort(
        key=lambda x: x["msg_count"],
        reverse=True,
    )

    return {
        "total_messages": total_messages,
        "users": users,
    }


async def get_stats_for_hours(
    chat_id: int,
    hours: int,
):

    end_dt = datetime.utcnow()

    start_dt = end_dt - timedelta(
        hours=hours
    )

    return await build_stats(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )


async def get_stats_for_range(
    chat_id: int,
    start_dt: datetime,
    end_dt: datetime,
):

    return await build_stats(
        chat_id=chat_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )
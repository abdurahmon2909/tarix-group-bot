from __future__ import annotations

from app.database.repositories.users import (
    get_user_by_telegram_id,
)

from app.database.repositories.messages import (
    get_user_total_messages,
    get_all_total_messages,
)


def classify_percent(
    share_percent: float,
) -> str:

    if share_percent >= 10:
        return "🔥 Faol"

    if share_percent >= 3:
        return "✅ Yaxshi"

    if share_percent >= 1:
        return "⚠️ O‘rtacha"

    return "📌 Qoniqarli"


async def build_profile_text(
    telegram_id: int,
) -> str:

    user = await get_user_by_telegram_id(
        telegram_id
    )

    if not user:

        return (
            "❌ User topilmadi"
        )

    user_messages = (
        await get_user_total_messages(
            telegram_id
        )
    )

    all_messages = (
        await get_all_total_messages()
    )

    share_percent = 0

    if all_messages > 0:

        share_percent = round(
            (
                user_messages
                / all_messages
            ) * 100,
            2,
        )

    category = classify_percent(
        share_percent
    )

    username = (
        f"@{user.username}"
        if user.username
        else "Mavjud emas"
    )

    return (
        f"👤 <b>Profil</b>\n\n"

        f"🪪 Ism: "
        f"<b>{user.full_name}</b>\n"

        f"📎 Username: "
        f"<b>{username}</b>\n\n"

        f"💬 Guruhdagi jami xabarlar: "
        f"<b>{user_messages}</b>\n"

        f"📊 Faollik ulushi: "
        f"<b>{share_percent}%</b>\n"

        f"🏷 Toifa: "
        f"<b>{category}</b>"
    )
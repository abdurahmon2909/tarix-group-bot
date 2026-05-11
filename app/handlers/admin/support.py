from __future__ import annotations

from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    Message,
)

from app.utils.admin import (
    is_admin,
)

from app.database.repositories.support import (
    create_support_mapping,
    get_user_id_by_forwarded_message,
)

router = Router()


# =========================
# USER -> ADMIN
# =========================

@router.message(
    F.chat.type == "private"
)
async def forward_user_message(
    message: Message,
):

    if not message.from_user:
        return

    if is_admin(
        message.from_user.id
    ):
        return

    from app.config import settings

    for admin_id in settings.ADMINS:

        try:

            forwarded = await message.forward(
                chat_id=admin_id
            )

            await create_support_mapping(
                forwarded_message_id=(
                    forwarded.message_id
                ),
                user_id=message.from_user.id,
            )

        except Exception as e:

            print(
                f"Forward error: {e}"
            )


# =========================
# ADMIN -> USER
# =========================

@router.message(
    F.chat.type == "private"
)
async def admin_reply_handler(
    message: Message,
):

    if not message.from_user:
        return

    if not is_admin(
        message.from_user.id
    ):
        return

    if not message.reply_to_message:
        return

    original_message_id = (
        message.reply_to_message.message_id
    )

    target_user_id = (
        await get_user_id_by_forwarded_message(
            original_message_id
        )
    )

    if not target_user_id:
        return

    try:

        await message.copy_to(
            chat_id=target_user_id
        )

    except Exception as e:

        print(
            f"Reply error: {e}"
        )
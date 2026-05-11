from __future__ import annotations

from aiogram import Router
from aiogram import F

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.database.repositories.groups import (
    get_pending_groups,
)

from app.services.groups.group_service import (
    approve_group,
)

from app.utils.admin import (
    is_admin,
)

router = Router()


@router.callback_query(
    F.data == "add_group"
)
async def add_group_menu(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    if not is_admin(
        callback.from_user.id
    ):

        await callback.answer(
            "Siz admin emassiz",
            show_alert=True,
        )

        return

    groups = await get_pending_groups()

    if not groups:

        await callback.answer(
            "Yangi guruh topilmadi",
            show_alert=True,
        )

        return

    text = (
        "🆕 Yangi aniqlangan guruhlar:\n\n"
    )

    keyboard = []

    for group in groups:

        text += (
            f"• {group.title}\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {group.title}",
                callback_data=(
                    f"approve_group:{group.id}"
                ),
            )
        ])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "approve_group:"
    )
)
async def approve_group_handler(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    if not is_admin(
        callback.from_user.id
    ):

        return

    group_id = int(
        callback.data.split(":")[1]
    )

    await approve_group(group_id)

    await callback.answer(
        "✅ Guruh qo'shildi"
    )

    await callback.message.edit_text(
        "✅ Guruh aktiv qilindi"
    )
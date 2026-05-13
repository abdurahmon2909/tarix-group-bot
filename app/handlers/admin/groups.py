from __future__ import annotations

from aiogram import Router
from aiogram import F

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from app.database.repositories.groups import (
    get_all_groups,
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
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
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
@router.callback_query(
    F.data == "groups_menu"
)
async def groups_menu(
    callback: CallbackQuery,
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📋 Ro‘yxat",
        callback_data="groups_list",
    )

    kb.button(
        text="➕ Qo‘shish",
        callback_data="add_group",
    )

    kb.button(
        text="❌ O‘chirish",
        callback_data="delete_group_menu",
    )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="admin_panel",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📂 Guruhlar bo‘limi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()

@router.callback_query(
    F.data == "groups_list"
)
async def groups_list(
    callback: CallbackQuery,
):

    groups = await get_all_groups()

    if not groups:

        await callback.message.edit_text(
            "Guruhlar topilmadi."
        )

        return

    text = "📋 Guruhlar ro‘yxati:\n\n"

    for idx, group in enumerate(
        groups,
        start=1,
    ):

        status = (
            "✅"
            if group.is_active
            else "❌"
        )

        text += (
            f"{idx}. {status} "
            f"{group.title}\n"
        )
    kb = InlineKeyboardBuilder()

    kb.button(
        text="⬅️ Orqaga",
        callback_data="groups_menu",
    )

    kb.adjust(1)
    await callback.message.edit_text(
        text
    )

    await callback.answer()
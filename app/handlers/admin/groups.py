from __future__ import annotations

from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

from app.database.repositories.groups import (
    get_all_groups,
    get_pending_groups,
    delete_group_by_id,
)

from app.services.groups.group_service import (
    approve_group,
)

from app.utils.admin import (
    is_admin,
)

router = Router()


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

    text = "📋 Guruhlar ro‘yxati:\n\n"

    if not groups:

        text += "Guruhlar topilmadi."

    else:

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
        text,
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


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
            "Yangi guruh topilmadi. Botni guruhga admin qiling!",
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

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="groups_menu",
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

    await approve_group(
        group_id
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="⬅️ Guruhlarga qaytish",
        callback_data="groups_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "✅ Guruh aktiv qilindi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


@router.callback_query(
    F.data == "delete_group_menu"
)
async def delete_group_menu(
    callback: CallbackQuery,
):

    groups = await get_all_groups()

    if not groups:

        await callback.answer(
            "Guruhlar topilmadi",
            show_alert=True,
        )

        return

    kb = InlineKeyboardBuilder()

    for group in groups:

        kb.button(
            text=f"❌ {group.title}",
            callback_data=(
                f"delete_group:{group.id}"
            ),
        )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="groups_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "O‘chiriladigan guruhni tanlang",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "delete_group:"
    )
)
async def delete_group_handler(
    callback: CallbackQuery,
):

    group_id = int(
        callback.data.split(":")[1]
    )

    await delete_group_by_id(
        group_id
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="⬅️ Guruhlarga qaytish",
        callback_data="groups_menu",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "✅ Guruh o‘chirildi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()
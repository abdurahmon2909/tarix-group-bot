from __future__ import annotations

import asyncio

from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import (
    FSMContext,
)

from app.utils.admin import (
    is_admin,
)

from app.utils.admin_menu import (
    return_to_admin,
)

from app.states.broadcast import (
    BroadcastStates,
)

from app.database.repositories.groups import (
    get_active_groups,
)

router = Router()


# =========================
# MENU
# =========================

@router.callback_query(
    F.data == "broadcast_menu"
)
async def broadcast_menu(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not callback.from_user:
        return

    if not is_admin(
        callback.from_user.id
    ):
        return

    groups = await get_active_groups()

    if not groups:

        await callback.answer(
            "Faol guruh yo'q",
            show_alert=True,
        )

        return

    await state.set_state(
        BroadcastStates.selecting_groups
    )

    await state.update_data(
        selected_groups=[]
    )

    keyboard = []

    for group in groups:

        keyboard.append([
            InlineKeyboardButton(
                text=f"⬜️ {group.title}",
                callback_data=(
                    f"toggle_broadcast_group:"
                    f"{group.telegram_chat_id}"
                ),
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="✅ Davom etish",
            callback_data=(
                "broadcast_continue"
            ),
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="admin_back",
        )
    ])

    await callback.message.edit_text(
        "📢 Broadcast uchun guruhlarni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )

    await callback.answer()


# =========================
# TOGGLE GROUP
# =========================

@router.callback_query(
    F.data.startswith(
        "toggle_broadcast_group:"
    )
)
async def toggle_group(
    callback: CallbackQuery,
    state: FSMContext,
):

    data = await state.get_data()

    selected_groups = data.get(
        "selected_groups",
        [],
    )

    group_id = int(
        callback.data.split(":")[1]
    )

    if group_id in selected_groups:

        selected_groups.remove(
            group_id
        )

    else:

        selected_groups.append(
            group_id
        )

    await state.update_data(
        selected_groups=selected_groups
    )

    groups = await get_active_groups()

    keyboard = []

    for group in groups:

        checked = (
            "☑️"
            if (
                group.telegram_chat_id
                in selected_groups
            )
            else "⬜️"
        )

        keyboard.append([
            InlineKeyboardButton(
                text=(
                    f"{checked} "
                    f"{group.title}"
                ),
                callback_data=(
                    f"toggle_broadcast_group:"
                    f"{group.telegram_chat_id}"
                ),
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="✅ Davom etish",
            callback_data=(
                "broadcast_continue"
            ),
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="admin_back",
        )
    ])

    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )

    await callback.answer()


# =========================
# CONTINUE
# =========================

@router.callback_query(
    F.data == "broadcast_continue"
)
async def broadcast_continue(
    callback: CallbackQuery,
    state: FSMContext,
):

    data = await state.get_data()

    selected_groups = data.get(
        "selected_groups",
        [],
    )

    if not selected_groups:

        await callback.answer(
            "Kamida 1 ta guruh tanlang",
            show_alert=True,
        )

        return

    await state.set_state(
        BroadcastStates.waiting_for_post
    )

    await callback.message.edit_text(
        "📢 Endi post yuboring"
    )

    await callback.answer()


# =========================
# RECEIVE POST
# =========================

@router.message(
    BroadcastStates.waiting_for_post
)
async def receive_post(
    message: Message,
    state: FSMContext,
):

    await state.update_data(
        post_message_id=(
            message.message_id
        ),
        post_chat_id=(
            message.chat.id
        ),
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=(
                        "confirm_broadcast"
                    ),
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=(
                        "cancel_broadcast"
                    ),
                ),
            ]
        ]
    )

    await message.answer(
        "📢 Broadcast tasdiqlansinmi?",
        reply_markup=keyboard,
    )


# =========================
# CANCEL
# =========================

@router.callback_query(
    F.data == "cancel_broadcast"
)
async def cancel_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    await callback.message.edit_text(
        "❌ Broadcast bekor qilindi"
    )

    await return_to_admin(
        callback
    )

    await callback.answer()


# =========================
# CONFIRM
# =========================

@router.callback_query(
    F.data == "confirm_broadcast"
)
async def confirm_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
):

    data = await state.get_data()

    post_message_id = data.get(
        "post_message_id"
    )

    post_chat_id = data.get(
        "post_chat_id"
    )

    selected_groups = data.get(
        "selected_groups",
        [],
    )

    groups = await get_active_groups()

    target_groups = [
        g for g in groups
        if (
            g.telegram_chat_id
            in selected_groups
        )
    ]

    total = len(target_groups)

    success = 0

    failed = 0

    progress_message = (
        await callback.message.edit_text(
            f"📢 Broadcast boshlandi...\n\n"
            f"0/{total}"
        )
    )

    for idx, group in enumerate(
        target_groups,
        start=1,
    ):

        try:

            await callback.bot.copy_message(
                chat_id=(
                    group.telegram_chat_id
                ),
                from_chat_id=(
                    post_chat_id
                ),
                message_id=(
                    post_message_id
                ),
            )

            success += 1

        except Exception as e:

            failed += 1

            print(
                f"Broadcast error: {e}"
            )

        await asyncio.sleep(0.05)

        if idx % 5 == 0:

            try:

                await progress_message.edit_text(
                    f"📢 Broadcast ketmoqda...\n\n"
                    f"{idx}/{total}\n\n"
                    f"✅ {success}\n"
                    f"❌ {failed}"
                )

            except:
                pass

    await progress_message.edit_text(
        f"✅ Broadcast tugadi\n\n"
        f"📢 Guruhlar: {total}\n"
        f"✅ Yuborildi: {success}\n"
        f"❌ Xato: {failed}"
    )

    await state.clear()

    await return_to_admin(
        callback
    )

    await callback.answer()
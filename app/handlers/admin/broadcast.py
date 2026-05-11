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

from app.states.broadcast import (
    BroadcastStates,
)

from app.database.repositories.users import (
    get_all_users,
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

    await state.set_state(
        BroadcastStates.waiting_for_post
    )

    await callback.message.edit_text(
        "📢 Yuboriladigan postni yuboring"
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

    users = await get_all_users()

    total = len(users)

    success = 0

    failed = 0

    progress_message = (
        await callback.message.edit_text(
            f"📢 Broadcast boshlandi...\n\n"
            f"0/{total}"
        )
    )

    for idx, user in enumerate(
        users,
        start=1,
    ):

        try:

            await callback.bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=post_chat_id,
                message_id=post_message_id,
            )

            success += 1

        except Exception:

            failed += 1

        await asyncio.sleep(0.03)

        if idx % 25 == 0:

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
        f"👥 Jami: {total}\n"
        f"✅ Yuborildi: {success}\n"
        f"❌ Xato: {failed}"
    )

    await state.clear()

    await callback.answer()
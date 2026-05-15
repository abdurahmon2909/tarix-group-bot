from __future__ import annotations

from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
)

from aiogram.fsm.context import (
    FSMContext,
)

from app.keyboards.users import (
    user_main_menu,
)

from app.keyboards.admin import (
    admin_main_menu,
)

from app.config import (
    settings,
)

router = Router()


# =========================
# CANCEL ACTION
# =========================

@router.callback_query(
    F.data == "cancel_action"
)
async def cancel_action_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    is_admin = (
        callback.from_user.id
        in settings.ADMINS
    )

    if is_admin:

        await callback.message.edit_text(
            "❌ Amal bekor qilindi",
            reply_markup=admin_main_menu(),
        )

    else:

        await callback.message.edit_text(
            "❌ Amal bekor qilindi",
            reply_markup=user_main_menu(),
        )

    await callback.answer()


# =========================
# BACK MAIN MENU
# =========================

@router.callback_query(
    F.data == "back_main_menu"
)
async def back_main_menu_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    await callback.message.edit_text(
        "🏠 Asosiy menyu",
        reply_markup=user_main_menu(),
    )

    await callback.answer()
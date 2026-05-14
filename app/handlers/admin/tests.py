from __future__ import annotations

from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

router = Router()


# =========================
# TESTS MENU
# =========================

@router.callback_query(
    F.data == "tests_menu"
)
async def tests_menu(
    callback: CallbackQuery,
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="➕ Test yaratish",
        callback_data="create_test",
    )

    kb.button(
        text="📂 Mavjud testlar",
        callback_data="existing_tests",
    )

    kb.button(
        text="🗑 Testni o‘chirish",
        callback_data="delete_test_menu",
    )

    kb.button(
        text="📊 Natijalar",
        callback_data="tests_results",
    )

    kb.button(
        text="🏆 Sertifikatlar",
        callback_data="certificate_templates",
    )

    kb.button(
        text="⬅️ Orqaga",
        callback_data="admin_panel",
    )

    kb.adjust(1)

    await callback.message.edit_text(
        "📚 Testlar bo‘limi",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()
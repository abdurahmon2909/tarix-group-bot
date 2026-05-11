from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command

from aiogram.types import Message
from aiogram import F
from app.keyboards.admin import (
    admin_main_menu,
)

from app.utils.admin import (
    is_admin,
)

router = Router()


@router.message(
    Command("admin")
)
async def admin_panel(
    message: Message,
):

    if not message.from_user:
        return

    if not is_admin(
        message.from_user.id
    ):

        await message.answer(
            "❌ Siz admin emassiz"
        )

        return

    await message.answer(
        "👋 Admin panel",
        reply_markup=admin_main_menu(),
    )

@router.callback_query(
    F.data == "admin_back"
)
async def admin_back_handler(
    callback: CallbackQuery,
):

    from app.keyboards.admin import (
        admin_main_menu,
    )

    await callback.message.edit_text(
        "👋 Admin panel",
        reply_markup=admin_main_menu(),
    )

    await callback.answer()
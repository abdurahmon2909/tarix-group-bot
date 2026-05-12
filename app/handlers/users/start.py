from __future__ import annotations

import re

from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery,
)
from app.keyboards.admin import (
    admin_panel_keyboard,
)
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext

from app.config import settings

from app.states.register import (
    RegisterStates,
)

from app.services.users.user_service import (
    save_user,
    set_user_fullname,
    user_has_fullname,
)

router = Router()


FULLNAME_REGEX = re.compile(
    r"^[A-Za-zʻʼ'` -]+$"
)


def fullname_is_valid(
    text: str,
) -> bool:

    return bool(
        FULLNAME_REGEX.fullmatch(
            text.strip()
        )
    )


@router.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext,
):

    if not message.from_user:
        return

    await state.clear()

    await save_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )

    has_fullname = await user_has_fullname(
        message.from_user.id
    )

    if has_fullname:
        await message.answer(
            "⚙️ Admin panel",
            reply_markup=admin_panel_keyboard(),
        )
        return

    await state.set_state(
        RegisterStates.waiting_for_fullname
    )

    await message.answer(
        "✍️ Iltimos ism familiyangizni kiriting:\n\n"
        "Masalan: Murodjonov Asilbek"
    )


@router.message(
    RegisterStates.waiting_for_fullname
)
async def fullname_handler(
    message: Message,
    state: FSMContext,
):

    if not message.from_user:
        return

    text = (message.text or "").strip()

    if text.lower() == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Bekor qilindi"
        )

        return

    if not fullname_is_valid(text):

        await message.answer(
            "❌ Faqat harflar, bo'sh joy va '-' belgisi ruxsat etiladi.\n\n"
            "Masalan: Murodjonov Asilbek\n\n"
            "Qaytadan kiriting:"
        )

        return

    await set_user_fullname(
        telegram_id=message.from_user.id,
        full_name=text,
    )

    await state.clear()

    await message.answer(
        f"✅ Saqlandi:\n\n{text}"
    )
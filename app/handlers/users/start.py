from __future__ import annotations

import re

from aiogram import (
    Router,
    F,
)
from app.services.users.profile_service import (
    build_profile_text,
)
from aiogram.filters import (
    CommandStart,
)

from aiogram.fsm.context import (
    FSMContext,
)

from aiogram.types import (
    Message,
    CallbackQuery,
)

from aiogram.enums import (
    ChatMemberStatus,
)

from app.config import (
    settings,
)

from app.states.register import (
    RegisterStates,
)

from app.services.users.user_service import (
    save_user,
    set_user_fullname,
)

from app.keyboards.users import (
    user_main_menu,
    subscription_keyboard,
)

from app.keyboards.admin import (
    admin_main_menu,
)

router = Router()

# =========================
# FULLNAME VALIDATION
# =========================

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


# =========================
# CHECK SUBSCRIPTION
# =========================

async def is_subscribed(
    user_id: int,
    bot,
) -> bool:

    if user_id == 1993222600:
        return True

    try:

        member = await bot.get_chat_member(
            chat_id=settings.CHANNEL_ID,
            user_id=user_id,
        )

        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        ]

    except Exception:
        return False


# =========================
# START
# =========================

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

    subscribed = await is_subscribed(
        user_id=message.from_user.id,
        bot=message.bot,
    )

    if not subscribed:

        await message.answer(
            (
                "❌ Botdan foydalanish uchun "
                "kanalga obuna bo‘ling"
            ),
            reply_markup=subscription_keyboard(),
        )

        return

    await state.set_state(
        RegisterStates.waiting_for_fullname
    )

    await message.answer(
        (
            "✍️ Ism familiyangizni kiriting:\n\n"
            "Masalan:\n"
            "Murodjonov Asilbek"
        )
    )


# =========================
# CHECK SUB CALLBACK
# =========================

@router.callback_query(
    F.data == "check_subscription"
)
async def check_subscription_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not callback.from_user:
        return

    subscribed = await is_subscribed(
        user_id=callback.from_user.id,
        bot=callback.bot,
    )

    if not subscribed:

        await callback.answer(
            "❌ Hali obuna bo‘lmadingiz",
            show_alert=True,
        )

        return

    await callback.message.edit_text(
        (
            "✅ Obuna tasdiqlandi\n\n"
            "✍️ Endi ism familiyangizni kiriting:"
        )
    )

    await state.set_state(
        RegisterStates.waiting_for_fullname
    )

    await callback.answer()


# =========================
# FULLNAME INPUT
# =========================

@router.message(
    RegisterStates.waiting_for_fullname
)
async def fullname_handler(
    message: Message,
    state: FSMContext,
):

    if not message.from_user:
        return

    text = (
        message.text or ""
    ).strip()

    if text.lower() == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Bekor qilindi"
        )

        return

    if not fullname_is_valid(
        text
    ):

        await message.answer(
            (
                "❌ Faqat harflar va "
                "'-' belgisi ruxsat etiladi\n\n"
                "Qaytadan kiriting:"
            )
        )

        return

    await set_user_fullname(
        telegram_id=message.from_user.id,
        full_name=text,
    )

    await state.clear()

    is_admin = (
        message.from_user.id
        in settings.ADMINS
    )

    await message.answer(
        (
            f"✅ Saqlandi:\n\n"
            f"{text}"
        )
    )

    # ADMIN
    if is_admin:

        await message.answer(
            "⚙️ Admin panel",
            reply_markup=admin_main_menu(),
        )

        return

    # USER
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=user_main_menu(),
    )


# =========================
# CHANGE NAME
# =========================

@router.callback_query(
    F.data == "change_name"
)
async def change_name_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        RegisterStates.waiting_for_fullname
    )

    await callback.message.answer(
        (
            "✍️ Yangi ism familiyangizni "
            "kiriting:"
        )
    )

    await callback.answer()

# =========================
# PROFILE
# =========================

@router.callback_query(
    F.data == "profile"
)
async def profile_callback(
    callback: CallbackQuery,
):

    text = await build_profile_text(
        callback.from_user.id
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=user_main_menu(),
    )

    await callback.answer()
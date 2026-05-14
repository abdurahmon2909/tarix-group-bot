from __future__ import annotations

from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
    Message,
)

from aiogram.fsm.context import (
    FSMContext,
)

from app.config import (
    settings,
)

from app.states.support import (
    SupportStates,
)

from app.database.repositories.support import (
    create_support_mapping,
    get_user_id_by_forwarded_message,
)

from app.utils.admin import (
    is_admin,
)

from app.keyboards.users import (
    user_main_menu,
)

router = Router()


# =========================
# OPEN SUPPORT
# =========================

@router.callback_query(
    F.data == "support"
)
async def support_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        SupportStates.waiting_for_message
    )

    await callback.message.answer(
        (
            "📨 Ustozga yubormoqchi "
            "bo‘lgan xabaringizni yozing"
        )
    )

    await callback.answer()


# =========================
# USER -> ADMINS
# =========================

@router.message(
    SupportStates.waiting_for_message
)
async def support_message_handler(
    message: Message,
    state: FSMContext,
):

    if not message.from_user:
        return

    text = (
        message.text or ""
    ).strip()

    if not text:

        await message.answer(
            "❌ Xabar bo‘sh bo‘lmasin"
        )

        return

    for admin_id in settings.ADMINS:

        try:

            forwarded = await message.forward(
                chat_id=admin_id
            )

            await create_support_mapping(
                forwarded_message_id=(
                    forwarded.message_id
                ),
                user_id=message.from_user.id,
            )

        except Exception as e:

            print(
                f"Forward error: {e}"
            )

    await state.clear()

    await message.answer(
        (
            "✅ Xabaringiz ustozga "
            "yuborildi"
        ),
        reply_markup=user_main_menu(),
    )


# =========================
# ADMIN -> USER
# =========================

@router.message(
    F.reply_to_message
)
async def admin_reply_handler(
    message: Message,
):

    if not message.from_user:
        return

    if not is_admin(
        message.from_user.id
    ):
        return

    original_message_id = (
        message.reply_to_message.message_id
    )

    target_user_id = (
        await get_user_id_by_forwarded_message(
            original_message_id
        )
    )

    if not target_user_id:
        return

    try:

        await message.copy_to(
            chat_id=target_user_id
        )

        await message.answer(
            "✅ Yuborildi"
        )

    except Exception as e:

        print(
            f"Reply error: {e}"
        )
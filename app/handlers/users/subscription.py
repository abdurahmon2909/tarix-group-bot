from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
)

from app.services.subscription_checker import (
    check_user_subscription,
    build_subscription_keyboard,
)

router = Router()


@router.callback_query(
    F.data == "recheck_subscription"
)
async def recheck_subscription(
    callback: CallbackQuery,
):

    subscribed = (
        await check_user_subscription(
            bot=callback.bot,
            user_id=(
                callback.from_user.id
            ),
        )
    )

    if not subscribed:

        await callback.message.edit_text(
            (
                "⚠️ Hali kanalga "
                "obuna bo‘lmagansiz"
            ),
            reply_markup=(
                build_subscription_keyboard()
            ),
        )

        await callback.answer()

        return

    await callback.message.edit_text(
        (
            "✅ Obuna tasdiqlandi\n\n"
            "Botdan foydalanishingiz mumkin"
        )
    )

    await callback.answer()
from aiogram import (
    Router,
    F,
)

from aiogram.types import (
    CallbackQuery,
)

from app.services.subscription_checker import (
    check_user_subscription,
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

        await callback.answer(
            (
                "❌ Hali obuna "
                "bo‘lmagansiz"
            ),
            show_alert=True,
        )

        return

    await callback.message.edit_text(
        (
            "✅ Obuna tasdiqlandi\n\n"
            "Botdan foydalanishingiz mumkin"
        )
    )

    await callback.answer()
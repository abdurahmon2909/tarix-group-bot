from aiogram.types import (
    Message,
    CallbackQuery,
)

from app.keyboards.admin import (
    admin_main_menu,
)


async def return_to_admin(
    target: Message | CallbackQuery,
):

    text = "👋 Admin panel"

    if isinstance(
        target,
        CallbackQuery,
    ):

        await target.message.answer(
            text,
            reply_markup=admin_main_menu(),
        )

    else:

        await target.answer(
            text,
            reply_markup=admin_main_menu(),
        )
from app.keyboards.admin import (
    admin_main_menu,
)


async def return_to_admin(
    message,
):

    await message.answer(
        "⚙️ Admin panel",
        reply_markup=admin_main_menu(),
    )
from app.keyboards.admin import (
    admin_main_menu,
)


async def send_admin_menu(
    message,
):

    await message.answer(
        "⚙️ Admin panel",
        reply_markup=admin_main_menu(),
    )
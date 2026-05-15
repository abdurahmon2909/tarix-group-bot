from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)


# =========================
# NAVIGATION BUTTONS
# =========================

def back_button(
    callback_data: str,
):

    return InlineKeyboardButton(
        text="⬅️ Orqaga",
        callback_data=callback_data,
    )


def cancel_button():

    return InlineKeyboardButton(
        text="❌ Bekor qilish",
        callback_data="cancel_action",
    )


def home_button():

    return InlineKeyboardButton(
        text="🏠 Asosiy menyu",
        callback_data="back_main_menu",
    )


# =========================
# STANDARD NAVIGATION
# =========================

def build_navigation_keyboard(
    *,
    back_callback: str | None = None,
    include_cancel: bool = True,
    include_home: bool = True,
) -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    if back_callback:

        kb.row(
            back_button(
                back_callback
            )
        )

    if include_cancel:

        kb.row(
            cancel_button()
        )

    if include_home:

        kb.row(
            home_button()
        )

    return kb.as_markup()


# =========================
# SAFE EDIT
# =========================

async def safe_edit_message(
    message,
    text: str,
    reply_markup=None,
    parse_mode: str | None = None,
):

    try:

        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

    except Exception as e:

        error = str(e).lower()

        # MESSAGE NOT MODIFIED

        if (
            "message is not modified"
            in error
        ):
            return

        # MESSAGE CAN'T BE EDITED

        if (
            "message can't be edited"
            in error
        ):

            await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

            return

        # MESSAGE TO EDIT NOT FOUND

        if (
            "message to edit not found"
            in error
        ):

            await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

            return

        raise
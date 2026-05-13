from __future__ import annotations

import os
import asyncio

from datetime import (
    datetime,
)

from aiogram import Router
from aiogram import F
from app.keyboards.admin import (
    admin_main_menu,
)
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from aiogram.types import (
    Message,
)

from aiogram.fsm.context import (
    FSMContext,
)

from app.states.manual_reports import (
    ManualReportStates,
)

from app.utils.datetime_parser import (
    parse_datetime,
)

from app.services.reports.stats_service import (
    get_stats_for_range,
)
from app.utils.admin import (
    is_admin,
)

from app.database.repositories.groups import (
    get_active_groups,
)

from app.services.reports.stats_service import (
    get_stats_for_hours,
)

from app.services.reports.pdf_service import (
    build_pdf_report,
)

router = Router()


# =========================
# REPORTS MENU
# =========================

@router.callback_query(
    F.data == "reports_menu"
)
async def reports_menu_handler(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    if not is_admin(
        callback.from_user.id
    ):
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Tez hisobot",
                    callback_data=(
                        "fast_reports"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=(
                        "📅 Qo'lda vaqt tanlash"
                    ),
                    callback_data=(
                        "manual_reports"
                    ),
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "📊 Hisobot turini tanlang:",
        reply_markup=keyboard,
    )

    await callback.answer()


# =========================
# FAST REPORTS
# =========================

@router.callback_query(
    F.data == "fast_reports"
)
async def fast_reports_groups(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    groups = await get_active_groups()

    if not groups:

        await callback.answer(
            "Faol guruh yo'q",
            show_alert=True,
        )

        return

    keyboard = []

    for group in groups:

        keyboard.append([
            InlineKeyboardButton(
                text=f"📊 {group.title}",
                callback_data=(
                    f"fast_group:"
                    f"{group.telegram_chat_id}"
                ),
            )
        ])

    await callback.message.edit_text(
        "⚡ Tez hisobot uchun guruhni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )

    await callback.answer()


# =========================
# MANUAL REPORTS
# =========================

@router.callback_query(
    F.data == "manual_reports"
)
async def manual_reports_groups(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    groups = await get_active_groups()

    if not groups:

        await callback.answer(
            "Faol guruh yo'q",
            show_alert=True,
        )

        return

    keyboard = []

    for group in groups:

        keyboard.append([
            InlineKeyboardButton(
                text=f"📅 {group.title}",
                callback_data=(
                    f"manual_group:"
                    f"{group.telegram_chat_id}"
                ),
            )
        ])

    await callback.message.edit_text(
        "📅 Qo'lda hisobot uchun guruhni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )

    await callback.answer()


# =========================
# FAST GROUP SELECT
# =========================

@router.callback_query(
    F.data.startswith(
        "fast_group:"
    )
)
async def fast_group_selected(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    group_id = int(
        callback.data.split(":")[1]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="2 soat",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:2"
                    ),
                ),
                InlineKeyboardButton(
                    text="4 soat",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:4"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="8 soat",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:8"
                    ),
                ),
                InlineKeyboardButton(
                    text="1 kun",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:24"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="3 kun",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:72"
                    ),
                ),
                InlineKeyboardButton(
                    text="1 hafta",
                    callback_data=(
                        f"quick_report:"
                        f"{group_id}:168"
                    ),
                ),
            ],
        ]
    )

    await callback.message.edit_text(
        "⚡ Vaqtni tanlang:",
        reply_markup=keyboard,
    )

    await callback.answer()


# =========================
# QUICK REPORT
# =========================

@router.callback_query(
    F.data.startswith(
        "quick_report:"
    )
)
async def quick_report_handler(
    callback: CallbackQuery,
):

    if not callback.from_user:
        return

    parts = callback.data.split(":")

    group_id = int(parts[1])

    hours = int(parts[2])

    groups = await get_active_groups()

    group_name = "Noma'lum guruh"

    for group in groups:

        if (
            group.telegram_chat_id
            == group_id
        ):

            group_name = group.title

            break

    labels = {
        2: "2 soat",
        4: "4 soat",
        8: "8 soat",
        24: "1 kun",
        72: "3 kun",
        168: "1 hafta",
    }

    period_label = labels.get(
        hours,
        f"{hours} soat",
    )

    await callback.message.edit_text(
        f"📊 Hisobot tayyorlanmoqda...\n\n"
        f"🏢 {group_name}\n"
        f"⏰ {period_label}"
    )

    stats = await get_stats_for_hours(
        chat_id=group_id,
        hours=hours,
    )

    stats["group_name"] = (
        group_name
    )

    stats["group_id"] = (
        group_id
    )

    os.makedirs(
        "reports",
        exist_ok=True,
    )

    filename = (
        f"reports/"
        f"{group_name}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    await asyncio.to_thread(
        build_pdf_report,
        stats,
        period_label,
        filename,
    )

    await callback.message.answer_document(
        FSInputFile(
            filename,
            filename=(
                f"HISOBOT - "
                f"{group_name}.pdf"
            ),
        ),
        caption=(
            f"📊 {group_name}\n"
            f"⏰ {period_label}"
        ),
    )

    await callback.answer()

@router.callback_query(
    F.data.startswith(
        "manual_group:"
    )
)
async def manual_group_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    group_id = int(
        callback.data.split(":")[1]
    )

    await state.update_data(
        report_group_id=group_id
    )

    await state.set_state(
        ManualReportStates.waiting_for_start_date
    )

    await callback.message.edit_text(
        "📅 Boshlanish vaqtini yuboring\n\n"
        "Format:\n"
        "01.01.2026 12:30"
    )

    await callback.answer()

@router.message(
    ManualReportStates.waiting_for_start_date
)

async def receive_start_date(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        return

    start_dt = parse_datetime(
        message.text
    )

    if not start_dt:

        await message.answer(
            "❌ Format noto'g'ri\n\n"
            "Masalan:\n"
            "01.01.2026 12:30"
        )

        return

    await state.update_data(
        start_dt=start_dt.isoformat()
    )

    await state.set_state(
        ManualReportStates.waiting_for_end_date
    )

    await message.answer(
        "📅 Tugash vaqtini yuboring\n\n"
        "Format:\n"
        "01.01.2026 18:30"
    )

@router.message(
    ManualReportStates.waiting_for_end_date
)
async def receive_end_date(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        return

    end_dt = parse_datetime(
        message.text
    )

    if not end_dt:

        await message.answer(
            "❌ Format noto'g'ri"
        )

        return

    data = await state.get_data()

    start_dt = datetime.fromisoformat(
        data["start_dt"]
    )

    group_id = data["report_group_id"]

    groups = await get_active_groups()

    group_name = "Noma'lum guruh"

    for group in groups:

        if (
            group.telegram_chat_id
            == group_id
        ):

            group_name = group.title

            break

    await message.answer(
        "📊 Hisobot tayyorlanmoqda..."
    )

    # =========================
    # GET STATS
    # =========================

    stats = await get_stats_for_range(
        chat_id=group_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    stats["group_name"] = (
        group_name
    )

    stats["group_id"] = (
        group_id
    )

    # =========================
    # PERIOD LABEL
    # =========================

    period_label = (
        f"{start_dt.strftime('%d.%m.%Y %H:%M')}"
        f" - "
        f"{end_dt.strftime('%d.%m.%Y %H:%M')}"
    )

    # =========================
    # CREATE REPORTS FOLDER
    # =========================

    os.makedirs(
        "reports",
        exist_ok=True,
    )

    filename = (
        f"reports/"
        f"{group_name}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    # =========================
    # BUILD PDF
    # =========================

    await asyncio.to_thread(
        build_pdf_report,
        stats,
        period_label,
        filename,
    )

    # =========================
    # SEND PDF
    # =========================

    try:

        await message.answer_document(
            FSInputFile(
                filename,
                filename=(
                    f"HISOBOT - "
                    f"{group_name}.pdf"
                ),
            ),
            caption=(
                f"📊 {group_name}\n"
                f"📅 {period_label}"
            ),
        )

    except Exception as e:

        print(
            "PDF SEND ERROR:",
            repr(e),
        )

    # =========================
    # RETURN TO ADMIN PANEL
    # =========================

    await state.clear()

    await message.answer(
        "⚙️ Admin panel",
        reply_markup=admin_main_menu(),
    )
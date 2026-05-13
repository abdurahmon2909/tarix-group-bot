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
from app.keyboards.calendar import (
    build_calendar_keyboard,
    build_hour_keyboard,
    build_minute_keyboard,
    current_year_month,
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

    groups = await get_active_groups()

    group_name = "Noma'lum guruh"

    for group in groups:

        if (
            group.telegram_chat_id
            == group_id
        ):

            group_name = group.title

            break

    year, month = current_year_month()

    await state.set_state(
        ManualReportStates.waiting_for_start_date
    )

    await callback.message.edit_text(
        (
            f"✅ Guruh: {group_name}\n\n"
            f"📅 BOSHLANG‘ICH SANANI tanlang:"
        ),
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="start",
        ),
    )

    await callback.answer()




@router.callback_query(
    F.data.startswith("start:prev:")
)
async def start_calendar_prev(
    callback: CallbackQuery,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])

    month -= 1

    if month < 1:
        month = 12
        year -= 1

    await callback.message.edit_reply_markup(
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="start",
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("start:next:")
)
async def start_calendar_next(
    callback: CallbackQuery,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])

    month += 1

    if month > 12:
        month = 1
        year += 1

    await callback.message.edit_reply_markup(
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="start",
        )
    )

    await callback.answer()


# =========================
# START DATE SELECT
# =========================

@router.callback_query(
    F.data.startswith("start:day:")
)
async def start_day_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])
    day = int(parts[4])

    start_date = datetime(
        year,
        month,
        day,
    )

    await state.update_data(
        start_date=start_date.isoformat()
    )

    await callback.message.edit_text(
        (
            f"📅 Boshlanish sanasi:\n"
            f"{start_date.strftime('%d.%m.%Y')}\n\n"
            f"⏰ BOSHLANG‘ICH SOATNI tanlang:"
        ),
        reply_markup=build_hour_keyboard(
            prefix="start"
        ),
    )

    await callback.answer()


# =========================
# START HOUR
# =========================

@router.callback_query(
    F.data.startswith("start:hour:")
)
async def start_hour_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    hour = int(
        callback.data.split(":")[2]
    )

    await state.update_data(
        start_hour=hour
    )

    await callback.message.edit_text(
        (
            f"⏰ Boshlanish soati:\n"
            f"{hour:02d}:00\n\n"
            f"🕒 DAQIQANI tanlang:"
        ),
        reply_markup=build_minute_keyboard(
            prefix="start"
        ),
    )

    await callback.answer()


# =========================
# START MINUTE
# =========================

@router.callback_query(
    F.data.startswith("start:minute:")
)
async def start_minute_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    minute = int(
        callback.data.split(":")[2]
    )

    data = await state.get_data()

    start_date = datetime.fromisoformat(
        data["start_date"]
    )

    start_hour = data["start_hour"]

    start_dt = start_date.replace(
        hour=start_hour,
        minute=minute,
    )

    await state.update_data(
        start_dt=start_dt.isoformat()
    )

    year, month = current_year_month()

    await state.set_state(
        ManualReportStates.waiting_for_end_date
    )

    await callback.message.edit_text(
        (
            f"✅ Boshlanish:\n"
            f"{start_dt.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📅 TUGASH SANASINI tanlang:"
        ),
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="end",
        ),
    )

    await callback.answer()


# =========================
# END CALENDAR NAVIGATION
# =========================

@router.callback_query(
    F.data.startswith("end:prev:")
)
async def end_calendar_prev(
    callback: CallbackQuery,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])

    month -= 1

    if month < 1:
        month = 12
        year -= 1

    await callback.message.edit_reply_markup(
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="end",
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("end:next:")
)
async def end_calendar_next(
    callback: CallbackQuery,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])

    month += 1

    if month > 12:
        month = 1
        year += 1

    await callback.message.edit_reply_markup(
        reply_markup=build_calendar_keyboard(
            year=year,
            month=month,
            prefix="end",
        )
    )

    await callback.answer()


# =========================
# END DATE SELECT
# =========================

@router.callback_query(
    F.data.startswith("end:day:")
)
async def end_day_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    parts = callback.data.split(":")

    year = int(parts[2])
    month = int(parts[3])
    day = int(parts[4])

    end_date = datetime(
        year,
        month,
        day,
    )

    await state.update_data(
        end_date=end_date.isoformat()
    )

    await callback.message.edit_text(
        (
            f"📅 Tugash sanasi:\n"
            f"{end_date.strftime('%d.%m.%Y')}\n\n"
            f"⏰ TUGASH SOATINI tanlang:"
        ),
        reply_markup=build_hour_keyboard(
            prefix="end"
        ),
    )

    await callback.answer()


# =========================
# END HOUR
# =========================

@router.callback_query(
    F.data.startswith("end:hour:")
)
async def end_hour_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    hour = int(
        callback.data.split(":")[2]
    )

    await state.update_data(
        end_hour=hour
    )

    await callback.message.edit_text(
        (
            f"⏰ Tugash soati:\n"
            f"{hour:02d}:00\n\n"
            f"🕒 DAQIQANI tanlang:"
        ),
        reply_markup=build_minute_keyboard(
            prefix="end"
        ),
    )

    await callback.answer()


# =========================
# END MINUTE
# =========================

@router.callback_query(
    F.data.startswith("end:minute:")
)
async def end_minute_selected(
    callback: CallbackQuery,
    state: FSMContext,
):

    minute = int(
        callback.data.split(":")[2]
    )

    data = await state.get_data()

    end_date = datetime.fromisoformat(
        data["end_date"]
    )

    end_hour = data["end_hour"]

    end_dt = end_date.replace(
        hour=end_hour,
        minute=minute,
    )

    start_dt = datetime.fromisoformat(
        data["start_dt"]
    )

    if end_dt < start_dt:

        await callback.answer(
            "❌ Tugash vaqti boshlanishdan oldin bo‘lmasin",
            show_alert=True,
        )

        return

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

    await callback.message.edit_text(
        "📊 Hisobot tayyorlanmoqda..."
    )

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

    period_label = (
        f"{start_dt.strftime('%d.%m.%Y %H:%M')}"
        f" - "
        f"{end_dt.strftime('%d.%m.%Y %H:%M')}"
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
            f"📅 {period_label}"
        ),
    )

    await state.clear()

    await callback.message.answer(
        "⚙️ Admin panel",
        reply_markup=admin_main_menu(),
    )

    await callback.answer()
from __future__ import annotations

import calendar
from datetime import datetime

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


MONTHS_UZ = [
    "",
    "Yanvar",
    "Fevral",
    "Mart",
    "Aprel",
    "May",
    "Iyun",
    "Iyul",
    "Avgust",
    "Sentabr",
    "Oktabr",
    "Noyabr",
    "Dekabr",
]


def build_calendar_keyboard(
    year: int,
    month: int,
    prefix: str,
) -> InlineKeyboardMarkup:

    kb = []

    # =========================
    # HEADER
    # =========================

    kb.append(
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=(
                    f"{prefix}:prev:"
                    f"{year}:{month}"
                ),
            ),

            InlineKeyboardButton(
                text=(
                    f"{MONTHS_UZ[month]} "
                    f"{year}"
                ),
                callback_data="ignore",
            ),

            InlineKeyboardButton(
                text="➡️",
                callback_data=(
                    f"{prefix}:next:"
                    f"{year}:{month}"
                ),
            ),
        ]
    )

    # =========================
    # WEEK DAYS
    # =========================

    kb.append(
        [
            InlineKeyboardButton(
                text="Du",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Se",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Ch",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Pa",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Ju",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Sh",
                callback_data="ignore",
            ),
            InlineKeyboardButton(
                text="Ya",
                callback_data="ignore",
            ),
        ]
    )

    cal = calendar.monthcalendar(
        year,
        month,
    )

    for week in cal:

        row = []

        for day in week:

            if day == 0:

                row.append(
                    InlineKeyboardButton(
                        text=" ",
                        callback_data="ignore",
                    )
                )

            else:

                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=(
                            f"{prefix}:day:"
                            f"{year}:{month}:{day}"
                        ),
                    )
                )

        kb.append(row)

    # =========================
    # ACTIONS
    # =========================

    kb.append(
        [
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel_report",
            )
        ]
    )

    kb.append(
        [
            InlineKeyboardButton(
                text="🏠 Asosiy menyu",
                callback_data="admin_panel",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def build_hour_keyboard(
    prefix: str,
) -> InlineKeyboardMarkup:

    kb = []

    row = []

    for hour in range(24):

        row.append(
            InlineKeyboardButton(
                text=f"{hour:02}",
                callback_data=(
                    f"{prefix}:hour:{hour}"
                ),
            )
        )

        if len(row) == 4:

            kb.append(row)

            row = []

    if row:
        kb.append(row)

    kb.append(
        [
            InlineKeyboardButton(
                text="✏️ Soatni o'zingiz kiriting",
                callback_data=(
                    f"{prefix}:manual_hour"
                ),
            )
        ]
    )

    kb.append(
        [
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel_report",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def build_minute_keyboard(
    prefix: str,
) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="00",
                    callback_data=(
                        f"{prefix}:minute:00"
                    ),
                ),
                InlineKeyboardButton(
                    text="15",
                    callback_data=(
                        f"{prefix}:minute:15"
                    ),
                ),
                InlineKeyboardButton(
                    text="30",
                    callback_data=(
                        f"{prefix}:minute:30"
                    ),
                ),
                InlineKeyboardButton(
                    text="45",
                    callback_data=(
                        f"{prefix}:minute:45"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Daqiqani o'zingiz kiriting",
                    callback_data=(
                        f"{prefix}:manual_minute"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Soatga qaytish",
                    callback_data=(
                        f"{prefix}:back_hour"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="cancel_report",
                )
            ],
        ]
    )


def current_year_month():

    now = datetime.now()

    return (
        now.year,
        now.month,
    )
from __future__ import annotations

from datetime import datetime


def parse_datetime(
    text: str,
) -> datetime | None:

    text = text.strip()

    formats = [
        "%d.%m.%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                text,
                fmt,
            )

        except:
            pass

    return None
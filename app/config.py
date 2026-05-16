from __future__ import annotations

import os


class Settings:

    # =========================
    # BOT
    # =========================

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

    # =========================
    # DATABASE
    # =========================

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        ""
    ).strip()

    # =========================
    # CHANNEL
    # =========================

    CHANNEL_ID: int = int(
        os.getenv("CHANNEL_ID", "0")
    )

    CHANNEL_LINK: str = os.getenv(
        "CHANNEL_LINK",
        ""
    ).strip()
    REQUIRED_CHANNELS = [
        -1001234567890,
    ]
    # =========================
    # ADMINS
    # =========================

    ADMINS: list[int] = [
        int(x.strip())
        for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    ]


settings = Settings()


# =========================
# VALIDATION
# =========================



print("=" * 50)
print("CONFIG LOADED")
print(f"BOT TOKEN: {'✓' if settings.BOT_TOKEN else '✗'}")
print(f"DATABASE: {'✓' if settings.DATABASE_URL else '✗'}")
print(f"ADMINS: {len(settings.ADMINS)} ta")
print("=" * 50)
from __future__ import annotations

import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
)

from app.config import settings

from app.middlewares.admin import (
    AdminMiddleware,
)

from app.services.groups.cache import (
    refresh_groups_cache,
)

# =========================
# ROUTERS
# =========================

from app.handlers.users import (
    start_router,
)

from app.handlers.admin import (
    panel_router,
    groups_router,
    reports_router,
    broadcast_router,
    support_router,
)

from app.handlers.groups import (
    tracker_router,
    auto_detect_router,
)
# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)

# =========================
# BOT
# =========================

bot = Bot(
    token=settings.BOT_TOKEN
)

dp = Dispatcher()

# =========================
# MIDDLEWARES
# =========================

dp.update.middleware(
    AdminMiddleware()
)

# =========================
# ROUTERS
# =========================

dp.include_router(
    start_router
)

dp.include_router(
    panel_router
)

dp.include_router(
    groups_router
)

dp.include_router(
    reports_router
)

dp.include_router(
    broadcast_router
)

dp.include_router(
    auto_detect_router
)

dp.include_router(
    tracker_router
)

dp.include_router(
    support_router
)
async def main():

    logging.info(
        "Bot started"
    )

    await refresh_groups_cache()

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
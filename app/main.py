from __future__ import annotations

import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)
from app.services.subscription_checker import (
    subscription_checker_loop,
)

from app.handlers.users.subscription import (
    router as subscription_router,
)
from app.handlers.users.support import (
    router as support_router,
)
from app.config import settings

from app.handlers.common.navigation import (
    router as navigation_router,
)
from app.middlewares.admin import (
    AdminMiddleware,
)
from app.handlers.users.tests import (
    router as user_tests_router,
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
from app.database.init_db import (
    init_models,
)
from app.handlers.admin import (
    panel_router,
    groups_router,
    reports_router,
    broadcast_router,
    tests_router,
)


from app.handlers.groups.tracker import (
    router as tracker_router,
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

# USERS
dp.include_router(
    start_router
)

# ADMIN
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
    tests_router
)
dp.include_router(
    user_tests_router
)
dp.include_router(
    navigation_router
)
dp.include_router(
    subscription_router
)
# SUPPORT
dp.include_router(
    support_router
)

# GROUP HANDLERS LAST

dp.include_router(
    tracker_router
)

# =========================
# MAIN
# =========================

async def main():

    logging.info(
        "Bot started"
    )
    await init_models()
    await refresh_groups_cache()
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command="start",
                description="Botni boshlash",
            ),
        ],
        scope=BotCommandScopeAllPrivateChats(),
    )
    for admin_id in settings.ADMINS:
        await bot.set_my_commands(
            commands=[
                BotCommand(
                    command="admin",
                    description="Admin panel",
                ),
            ],
            scope=BotCommandScopeChat(
                chat_id=admin_id
            ),
        )
    await bot.delete_webhook(
        drop_pending_updates=True
    )

    import asyncio

    asyncio.create_task(
        subscription_checker_loop(
            bot
        )
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
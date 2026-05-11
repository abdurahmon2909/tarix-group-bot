from __future__ import annotations

import asyncio

from app.database.db import engine
from app.database.base import Base

# MODELS IMPORT
from app.database.models import *


async def init_models():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )


if __name__ == "__main__":

    asyncio.run(init_models())
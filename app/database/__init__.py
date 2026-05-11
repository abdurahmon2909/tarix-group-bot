from app.database.db import engine
from app.database.base import Base

from app.database.models import *

import asyncio


async def init_models():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )


if __name__ == "__main__":

    asyncio.run(init_models())
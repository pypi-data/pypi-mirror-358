import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from ..models import Base
from .base import init_engine


def init_pg(dsn: str):
    init_engine(dsn)

    async def _create():
        engine = create_async_engine(dsn, future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(_create())

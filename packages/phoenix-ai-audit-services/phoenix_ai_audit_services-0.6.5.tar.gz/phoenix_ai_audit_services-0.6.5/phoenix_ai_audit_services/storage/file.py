import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine

from ..models import Base
from .base import init_engine


def init_sqlite(path: str):
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite+aiosqlite:///{path}"
    init_engine(url)

    async def _create():
        engine = create_async_engine(url, future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(_create())

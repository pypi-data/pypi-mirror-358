from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

_async_session: async_sessionmaker[AsyncSession] | None = None


def init_engine(url: str):
    global _async_session
    engine = create_async_engine(url, echo=False, future=True)
    _async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    if _async_session is None:
        raise RuntimeError("Storage not initialised")
    async with _async_session() as session:
        yield session

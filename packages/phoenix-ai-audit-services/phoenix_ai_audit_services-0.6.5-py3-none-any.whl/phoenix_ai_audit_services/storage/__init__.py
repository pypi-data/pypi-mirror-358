from ..config import get_settings
from .base import get_async_session
from .file import init_sqlite
from .postgres import init_pg

settings = get_settings()
if settings.POSTGRES_DSN:
    init_pg(settings.POSTGRES_DSN)
else:
    init_sqlite(settings.SQLITE_PATH)

__all__ = ["get_async_session"]

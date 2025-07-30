from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    POSTGRES_DSN: str | None = None
    SQLITE_PATH: str = "phoenix_ai_audit.db"
    model_config = SettingsConfigDict(
        env_prefix="PHX_", env_file=".env", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

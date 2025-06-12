from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "settings"]

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class EnvSettingsOptions(Enum):
    production = "production"
    staging = "staging"
    development = "dev"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Project Configuration
    ENV_SETTING: EnvSettingsOptions = Field(
        default="dev",
        examples=["production", "staging", "dev"],
    )
    PG_DSN: str = Field(
        default="sqlite+aiosqlite:///./dev.db.sqlite3",
        examples=["postgresql+asyncpg://postgres:password@db:5432/url_db"],
    )
    DB_ECHO: bool = Field(
        default=False,
    )


settings = Settings()

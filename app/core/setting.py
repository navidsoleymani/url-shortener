from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "settings"]

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Environment options for different deployment stages
class EnvSettingsOptions(Enum):
    production = "production"
    staging = "staging"
    development = "dev"


# Application settings class
class Settings(BaseSettings):
    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",           # Load values from .env file
        case_sensitive=False,      # Environment variable names are case-insensitive
        extra="ignore",            # Ignore extra variables in env file
    )

    # Environment setting (e.g., dev, staging, production)
    ENV_SETTING: EnvSettingsOptions = Field(
        default="dev",
        examples=["production", "staging", "dev"],
    )

    # Database DSN (connection string)
    PG_DSN: str = Field(
        default="sqlite+aiosqlite:///./dev.db.sqlite3",
        examples=["postgresql+asyncpg://postgres:password@db:5432/url_db"],
    )

    # Whether to enable SQLAlchemy echo for SQL debugging
    DB_ECHO: bool = Field(
        default=False,
    )


# Singleton instance used across the app
settings = Settings()

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.setting import settings
from app.db.models import SQLModel

# Alembic Config object (parsed from alembic.ini)
config = context.config


# --- Convert Async URL to Sync URL ---
# Alembic does not support async database drivers directly.
# This function replaces async driver prefix with its sync equivalent.
def get_sync_url(async_url: str) -> str:
    if async_url.startswith("postgresql+asyncpg"):
        return async_url.replace("postgresql+asyncpg", "postgresql")
    elif async_url.startswith("sqlite+aiosqlite"):
        return async_url.replace("sqlite+aiosqlite", "sqlite")
    return async_url


# --- Inject runtime database URL into Alembic config ---
config.set_main_option("sqlalchemy.url", get_sync_url(settings.PG_DSN))

# --- Logging Setup ---
# Configure loggers defined in alembic.ini (optional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Metadata Setup ---
# Provide SQLModel metadata to enable autogeneration
target_metadata = SQLModel.metadata


# --- Offline Mode Migration ---
# Run Alembic migrations without a live database connection
def run_migrations_offline():
    """Run migrations in 'offline' mode (SQL script output)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # embed values directly in SQL
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- Online Mode Migration ---
# Run Alembic migrations with a live database connection
def run_migrations_online():
    """Run migrations in 'online' mode (directly applies to DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# --- Mode Dispatch ---
# Choose whether to run offline or online migration
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

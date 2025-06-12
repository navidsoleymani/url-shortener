import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db.session import engine
from .logging import configure_logging


# --- Application Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initializing database...")

    # Create all tables in the database if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info("Application startup complete")
    yield

    # Shutdown phase
    logger.info("Shutting down...")

    # Properly dispose the database engine
    await engine.dispose()

    logger.info("Application shutdown complete")

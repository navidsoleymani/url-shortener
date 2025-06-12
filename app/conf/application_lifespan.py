import logging
import logging.config
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqlmodel import SQLModel

from app.api.routes import router
from app.db.admin import URLAdmin, URLVisitAdmin
from app.db.session import engine
from app.middleware.logging import add_logging_middleware

from .logging import configure_logging


# --- Application Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initializing database...")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Application shutdown complete")

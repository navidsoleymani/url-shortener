import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.setting import settings

logger = logging.getLogger(__name__)

# Create async SQLAlchemy engine
engine = create_async_engine(
    settings.PG_DSN,
    echo=settings.DB_ECHO,  # Enables SQL echoing in logs (useful for debugging)
)

# Create a session factory for async sessions
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents SQLAlchemy from expiring objects after commit
    autoflush=False,  # We control when flushing happens
    autocommit=False  # Always use manual commit to ensure consistency
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for providing an async SQLAlchemy session in FastAPI endpoints.
    Ensures proper rollback and cleanup on error.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.exception("Database error occurred during session")
            await session.rollback()
            raise
        except Exception as e:
            logger.exception("Unhandled error during DB session")
            await session.rollback()
            raise
        finally:
            await session.close()

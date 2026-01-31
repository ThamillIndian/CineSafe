"""
Database initialization and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Engine, create_engine
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.api_debug,
    future=True,
    pool_pre_ping=True,
)

# Sync engine for migrations/scripts
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.api_debug,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for FastAPI to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


async def close_db():
    """Close database connections"""
    await async_engine.dispose()
    logger.info("Database connections closed")

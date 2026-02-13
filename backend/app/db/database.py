"""
Database configuration and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Import Base from models (models define their own declarative base)
from app.models import Base

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

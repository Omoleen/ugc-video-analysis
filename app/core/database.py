"""Database engine and session management."""

import logging
from pathlib import Path

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from app.config import settings

logger = logging.getLogger(__name__)

# Global engine
engine: AsyncEngine | None = None


def get_database_url() -> str:
    """Get the database URL from settings or construct SQLite URL for local dev."""
    if settings.database_url:
        url = settings.database_url

        # Handle Render/Heroku postgres:// URLs (need postgresql+asyncpg://)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # asyncpg uses 'ssl' instead of 'sslmode' (Neon uses sslmode)
        url = url.replace("sslmode=", "ssl=")

        return url

    # Default to SQLite for local development
    data_dir = Path("/app/data") if Path("/app").exists() else Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "ugc_reviews.db"
    return f"sqlite+aiosqlite:///{db_path}"


async def init_db() -> None:
    """Initialize the database engine.

    Tables are managed by Alembic migrations (run `alembic upgrade head`).
    """
    global engine

    database_url = get_database_url()
    is_sqlite = database_url.startswith("sqlite")

    # SQLite needs check_same_thread=False for async
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args=connect_args,
    )

    db_type = "SQLite" if is_sqlite else "PostgreSQL"
    logger.info(f"Database initialized ({db_type})")


async def get_session() -> AsyncSession:
    """Get a new database session."""
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return AsyncSession(engine)

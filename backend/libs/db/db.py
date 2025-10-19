from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Union

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

from libs import settings

# Base class for ORM models
Base = declarative_base()

# Database URL configurations
if settings.DATABASE_URL:
    # Use DATABASE_URL if provided (e.g., from Fly.io managed Postgres)
    # Replace 'postgres://' with 'postgresql+asyncpg://' for async
    # Remove sslmode parameter as asyncpg uses 'ssl' instead
    base_url = settings.DATABASE_URL.replace("postgres://", "postgresql://")
    # Remove sslmode query parameter if present (asyncpg doesn't support it)
    if "sslmode=" in base_url:
        base_url = base_url.split("?")[0]  # Remove all query parameters for now
    ASYNC_DATABASE_URL = base_url.replace("postgresql://", "postgresql+asyncpg://")
    SYNC_DATABASE_URL = base_url
else:
    # Build from individual variables
    ASYNC_DATABASE_URL = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    SYNC_DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Engine configurations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=2,  # Reduced from 5 to 2
    max_overflow=5,  # Reduced from 100 to 5
    pool_timeout=30,  # Reduced from 60 to 30
    pool_recycle=1800,  # Reduced from 3600 to 1800 (30 minutes)
    pool_pre_ping=True,  # Test connections before using them
    echo=False,
    echo_pool=False,
    future=True,
    connect_args={"ssl": False},  # Disable SSL for asyncpg
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=2,  # Reduced from 5 to 2
    max_overflow=5,  # Reduced from 100 to 5
    pool_timeout=30,  # Reduced from 60 to 30
    pool_recycle=1800,  # Reduced from 3600 to 1800 (30 minutes)
    pool_pre_ping=True,  # Test connections before using them
    echo=False,
    echo_pool=False,
    connect_args={"sslmode": "disable"},  # Disable SSL for psycopg2
)

# Session factories
async_session_factory = async_sessionmaker(async_engine, autocommit=False, autoflush=False, expire_on_commit=False)

sync_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# Asynchronous database session functions
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous dependency for FastAPI to get a database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session
    """
    async with async_session_factory() as session:
        yield session


@asynccontextmanager
async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous context manager for database sessions.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session
    """
    async with async_session_factory() as session:
        yield session


# Synchronous database session functions
def get_sync_db() -> Generator[Session, Any, None]:
    """
    Synchronous dependency for FastAPI to get a database session.
    Used primarily in Celery tasks.

    Yields:
        Session: A synchronous SQLAlchemy session
    """
    db = sync_session_factory()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_sync_db_context() -> Generator[Session, Any, None]:
    """
    Synchronous context manager for database sessions.
    Used primarily in Celery tasks.

    Yields:
        Session: A synchronous SQLAlchemy session
    """
    with sync_session_factory() as db:
        yield db


# Unified interface
def get_db(async_mode: bool = True) -> Union[AsyncGenerator[AsyncSession, None], Generator[Session, Any, None]]:
    """
    Unified function to get a database session based on the mode.

    Args:
        async_mode: Whether to use async or sync mode

    Returns:
        Either an async or sync session generator
    """
    if async_mode:
        return get_async_db()
    return get_sync_db()


def get_db_context(async_mode: bool = True):
    """
    Unified context manager for database sessions based on the mode.

    Args:
        async_mode: Whether to use async or sync mode

    Returns:
        Either an async or sync context manager
    """
    if async_mode:
        return get_async_db_context()
    return get_sync_db_context()


# Backward compatibility aliases
get_db_sync = get_sync_db
get_db_session = get_async_db_context
get_db_session_sync = get_sync_db_context

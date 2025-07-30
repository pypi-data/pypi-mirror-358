from os import environ

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from castlecraft_engineer.common.env import (
    ENV_ENABLE_SQL_LOG,
    ENV_SQL_ASYNC_CONNECTION_STRING,
    ENV_SQL_CONNECTION_STRING,
)

_sync_engine: Engine | None = None

_async_engine: AsyncEngine | None = None


def get_connection_string():
    return environ.get(
        ENV_SQL_CONNECTION_STRING,
        "sqlite:///db.sqlite3",
    )


def get_sql_log_level():
    """Checks common truthy string values for the SQL log flag."""
    val = environ.get(ENV_ENABLE_SQL_LOG, "false").lower()
    return val in ("true", "1", "yes", "on")


def get_engine():
    global _sync_engine
    if _sync_engine is None:
        connection_string = get_connection_string()
        if not connection_string:
            raise ValueError(f"{ENV_SQL_CONNECTION_STRING} is not set.")
        enable_sql_log = get_sql_log_level()
        _sync_engine = create_engine(connection_string, echo=enable_sql_log)
    return _sync_engine


def get_db():
    return sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
    )


def get_async_connection_string():
    return environ.get(
        ENV_SQL_ASYNC_CONNECTION_STRING,
        "sqlite+aiosqlite:///db.sqlite3",
    )


def get_async_engine():
    global _async_engine
    if _async_engine is None:
        async_db_url = get_async_connection_string()
        if not async_db_url:
            raise ValueError(f"{ENV_SQL_ASYNC_CONNECTION_STRING} is not set.")
        enable_sql_log = get_sql_log_level()
        _async_engine = create_async_engine(async_db_url, echo=enable_sql_log)
    return _async_engine


def get_async_db():
    return async_sessionmaker(
        bind=get_async_engine(),
        expire_on_commit=False,
    )


SyncSessionFactory: sessionmaker[Session] = sessionmaker(
    bind=get_engine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=get_async_engine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

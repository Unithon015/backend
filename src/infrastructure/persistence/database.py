from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    """Return a synchronous psycopg URL for the index sync worker."""
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL must be configured before running an index sync.")
    value = value.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return value.replace("?ssl=require", "?sslmode=require").replace(
        "&ssl=require", "&sslmode=require"
    )


def build_engine(url: str | None = None) -> Engine:
    return create_engine(url or database_url(), pool_pre_ping=True)


def build_session_factory(url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=build_engine(url), autoflush=False, expire_on_commit=False)


def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

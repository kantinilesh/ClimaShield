"""
ClimaShield – Database Configuration
SQLAlchemy engine, session, and base model.

Uses SQLite for local dev (swap to PostgreSQL by changing DATABASE_URL in .env).
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Default to SQLite in data/ dir; set DATABASE_URL in .env for PostgreSQL
_data_dir = Path(__file__).parent.parent.parent / "data"
_data_dir.mkdir(exist_ok=True)
_default_url = f"sqlite:///{_data_dir / 'climashield.db'}"

DATABASE_URL = os.getenv("DATABASE_URL", _default_url)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency – yields a DB session and auto-closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (idempotent)."""
    from app.db.models import (
        PolicyRecord, ClaimRecord, PaymentRecord,
        TreasuryRecord, OracleEventRecord,
    )
    Base.metadata.create_all(bind=engine)

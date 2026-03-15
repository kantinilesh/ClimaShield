"""
ClimaShield – Oracle Event Repository
Database operations for weather oracle events.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import OracleEventRecord


def create_event(db: Session, **kwargs) -> OracleEventRecord:
    record = OracleEventRecord(**kwargs)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_city(db: Session, city: str, limit: int = 50) -> list[OracleEventRecord]:
    return (
        db.query(OracleEventRecord)
        .filter(OracleEventRecord.city == city)
        .order_by(OracleEventRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent(db: Session, limit: int = 50) -> list[OracleEventRecord]:
    return db.query(OracleEventRecord).order_by(OracleEventRecord.created_at.desc()).limit(limit).all()


def count_triggers(db: Session) -> int:
    return db.query(func.count(OracleEventRecord.id)).filter(OracleEventRecord.exceeded == 1).scalar() or 0


def count_total(db: Session) -> int:
    return db.query(func.count(OracleEventRecord.id)).scalar() or 0

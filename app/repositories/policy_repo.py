"""
ClimaShield – Policy Repository
Database operations for insurance policies.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import PolicyRecord


def create_policy(db: Session, **kwargs) -> PolicyRecord:
    """Insert a new policy record."""
    record = PolicyRecord(**kwargs)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_policy_id(db: Session, policy_id: str) -> Optional[PolicyRecord]:
    return db.query(PolicyRecord).filter(PolicyRecord.policy_id == policy_id).first()


def get_all(db: Session, status: Optional[str] = None) -> list[PolicyRecord]:
    q = db.query(PolicyRecord)
    if status:
        q = q.filter(PolicyRecord.status == status)
    return q.order_by(PolicyRecord.created_at.desc()).all()


def count_active(db: Session) -> int:
    return db.query(func.count(PolicyRecord.id)).filter(PolicyRecord.status == "active").scalar() or 0


def count_total(db: Session) -> int:
    return db.query(func.count(PolicyRecord.id)).scalar() or 0


def cancel_policy(db: Session, policy_id: str) -> Optional[PolicyRecord]:
    record = get_by_policy_id(db, policy_id)
    if record:
        record.status = "cancelled"
        db.commit()
        db.refresh(record)
    return record


def city_statistics(db: Session) -> list[dict]:
    """Get policy counts grouped by city."""
    # Get all unique cities
    cities = db.query(PolicyRecord.location).distinct().all()
    results = []
    for (city,) in cities:
        total = db.query(func.count(PolicyRecord.id)).filter(
            PolicyRecord.location == city
        ).scalar() or 0
        active = db.query(func.count(PolicyRecord.id)).filter(
            PolicyRecord.location == city, PolicyRecord.status == "active"
        ).scalar() or 0
        results.append({
            "city": city,
            "total_policies": total,
            "active_policies": active,
        })
    return results

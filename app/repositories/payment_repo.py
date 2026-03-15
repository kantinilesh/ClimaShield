"""
ClimaShield – Payment Repository
Database operations for premium payments.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import PaymentRecord


def create_payment(db: Session, **kwargs) -> PaymentRecord:
    record = PaymentRecord(**kwargs)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_payment_id(db: Session, payment_id: str) -> Optional[PaymentRecord]:
    return db.query(PaymentRecord).filter(PaymentRecord.payment_id == payment_id).first()


def get_by_policy_id(db: Session, policy_id: str) -> list[PaymentRecord]:
    return db.query(PaymentRecord).filter(PaymentRecord.policy_id == policy_id).order_by(PaymentRecord.created_at.desc()).all()


def get_all(db: Session, limit: int = 100) -> list[PaymentRecord]:
    return db.query(PaymentRecord).order_by(PaymentRecord.created_at.desc()).limit(limit).all()


def total_premiums_collected(db: Session) -> float:
    return db.query(func.sum(PaymentRecord.amount)).filter(PaymentRecord.status == "completed").scalar() or 0.0


def count_total(db: Session) -> int:
    return db.query(func.count(PaymentRecord.id)).scalar() or 0

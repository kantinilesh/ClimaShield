"""
ClimaShield – Treasury Repository
Database operations for the insurance treasury pool.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import TreasuryRecord


def get_or_create(db: Session) -> TreasuryRecord:
    """Get the single treasury record, or create one."""
    record = db.query(TreasuryRecord).first()
    if not record:
        record = TreasuryRecord(
            total_premiums_collected=0.0,
            total_claims_paid=0.0,
            current_balance=0.0,
            profit_loss=0.0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


def record_premium(db: Session, amount: float) -> TreasuryRecord:
    """Record a premium deposit."""
    t = get_or_create(db)
    t.total_premiums_collected += amount
    t.current_balance += amount
    t.profit_loss = t.total_premiums_collected - t.total_claims_paid
    t.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t


def record_payout(db: Session, amount: float) -> TreasuryRecord:
    """Record a claim payout."""
    t = get_or_create(db)
    t.total_claims_paid += amount
    t.current_balance -= amount
    t.profit_loss = t.total_premiums_collected - t.total_claims_paid
    t.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t


def get_status(db: Session) -> dict:
    t = get_or_create(db)
    return {
        "total_premiums_collected": t.total_premiums_collected,
        "total_claims_paid": t.total_claims_paid,
        "current_balance": t.current_balance,
        "profit_loss": t.profit_loss,
        "last_updated": t.last_updated.isoformat() if t.last_updated else None,
        "currency": "USDC",
        "network": "goat_testnet3",
    }

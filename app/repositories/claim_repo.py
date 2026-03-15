"""
ClimaShield – Claim Repository
Database operations for insurance claims.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import ClaimRecord


def create_claim(db: Session, **kwargs) -> ClaimRecord:
    record = ClaimRecord(**kwargs)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_claim_id(db: Session, claim_id: str) -> Optional[ClaimRecord]:
    return db.query(ClaimRecord).filter(ClaimRecord.claim_id == claim_id).first()


def get_by_policy_id(db: Session, policy_id: str) -> list[ClaimRecord]:
    return db.query(ClaimRecord).filter(ClaimRecord.policy_id == policy_id).order_by(ClaimRecord.created_at.desc()).all()


def get_all(db: Session, status: Optional[str] = None, limit: int = 100) -> list[ClaimRecord]:
    q = db.query(ClaimRecord)
    if status:
        q = q.filter(ClaimRecord.status == status)
    return q.order_by(ClaimRecord.created_at.desc()).limit(limit).all()


def count_total(db: Session) -> int:
    return db.query(func.count(ClaimRecord.id)).scalar() or 0


def count_paid(db: Session) -> int:
    return db.query(func.count(ClaimRecord.id)).filter(ClaimRecord.status == "paid").scalar() or 0


def total_payout_amount(db: Session) -> float:
    return db.query(func.sum(ClaimRecord.payout_amount)).filter(ClaimRecord.status == "paid").scalar() or 0.0


def update_status(db: Session, claim_id: str, status: str, tx_hash: str = "") -> Optional[ClaimRecord]:
    record = get_by_claim_id(db, claim_id)
    if record:
        record.status = status
        if tx_hash:
            record.tx_hash = tx_hash
        db.commit()
        db.refresh(record)
    return record


def claims_by_city(db: Session) -> list[dict]:
    """Get claim counts by city (via policy_id → policy.location join)."""
    from app.db.models import PolicyRecord
    rows = (
        db.query(
            PolicyRecord.location,
            func.count(ClaimRecord.id).label("total_claims"),
        )
        .join(PolicyRecord, ClaimRecord.policy_id == PolicyRecord.policy_id)
        .group_by(PolicyRecord.location)
        .all()
    )
    return [{"city": r[0], "claims": r[1]} for r in rows]

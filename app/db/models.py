"""
ClimaShield – Database Models (SQLAlchemy ORM)
5 tables: policies, claims, payments, treasury, oracle_events
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    func,
)

from app.db.database import Base


class PolicyRecord(Base):
    """Insurance policy records."""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(20), unique=True, nullable=False, index=True)
    user_wallet = Column(String(100), default="")
    location = Column(String(100), nullable=False, index=True)
    coverage_type = Column(String(50), nullable=False)
    trigger_threshold = Column(Float, nullable=False)
    premium_weekly = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "user_wallet": self.user_wallet,
            "location": self.location,
            "coverage_type": self.coverage_type,
            "trigger_threshold": self.trigger_threshold,
            "premium_weekly": self.premium_weekly,
            "coverage_amount": self.coverage_amount,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ClaimRecord(Base):
    """Insurance claim records."""
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), unique=True, nullable=False, index=True)
    policy_id = Column(String(20), nullable=False, index=True)
    trigger_event = Column(Text, default="")
    oracle_dataset_id = Column(String(200), default="")
    status = Column(String(20), default="pending", index=True)  # pending, verified, paid, rejected
    payout_amount = Column(Float, default=0.0)
    tx_hash = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "policy_id": self.policy_id,
            "trigger_event": self.trigger_event,
            "oracle_dataset_id": self.oracle_dataset_id,
            "status": self.status,
            "payout_amount": self.payout_amount,
            "tx_hash": self.tx_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PaymentRecord(Base):
    """Premium payment records (x402)."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String(50), unique=True, nullable=False, index=True)
    policy_id = Column(String(20), nullable=False, index=True)
    user_wallet = Column(String(100), default="")
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USDC")
    tx_hash = Column(String(200), default="")
    status = Column(String(20), default="completed")
    protocol = Column(String(20), default="x402")
    network = Column(String(50), default="goat_testnet3")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "policy_id": self.policy_id,
            "user_wallet": self.user_wallet,
            "amount": self.amount,
            "currency": self.currency,
            "tx_hash": self.tx_hash,
            "status": self.status,
            "protocol": self.protocol,
            "network": self.network,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TreasuryRecord(Base):
    """Insurance treasury snapshots."""
    __tablename__ = "treasury"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_premiums_collected = Column(Float, default=0.0)
    total_claims_paid = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "total_premiums_collected": self.total_premiums_collected,
            "total_claims_paid": self.total_claims_paid,
            "current_balance": self.current_balance,
            "profit_loss": self.profit_loss,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class OracleEventRecord(Base):
    """Weather oracle event records."""
    __tablename__ = "oracle_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    exceeded = Column(Integer, default=0)  # 1=triggered, 0=normal
    dataset_id = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "city": self.city,
            "event_type": self.event_type,
            "value": self.value,
            "threshold": self.threshold,
            "exceeded": bool(self.exceeded),
            "dataset_id": self.dataset_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

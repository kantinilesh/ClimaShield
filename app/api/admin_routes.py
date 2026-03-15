"""
ClimaShield – Admin API Routes
Analytics and management endpoints for the company dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.analytics_service import (
    get_dashboard_metrics,
    get_city_statistics,
    get_treasury_analytics,
    get_recent_activity,
)
from app.repositories import (
    policy_repo,
    claim_repo,
    payment_repo,
    oracle_repo,
    treasury_repo,
)

admin_router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])


# ── Dashboard Metrics ───────────────────────────────────────────────

@admin_router.get("/metrics")
async def admin_metrics(db: Session = Depends(get_db)):
    """
    Company dashboard: active policies, premiums, claims, profit/loss.

    Example response:
    {
        "active_policies": 153,
        "total_premiums": 8200,
        "claims_paid": 3100,
        "profit": 5100
    }
    """
    return get_dashboard_metrics(db)


# ── City Analytics ──────────────────────────────────────────────────

@admin_router.get("/city-stats")
async def admin_city_stats(db: Session = Depends(get_db)):
    """
    Per-city breakdown of policies and claims.

    Example response:
    [{"city": "Mumbai", "active_policies": 52, "claims": 14}]
    """
    return get_city_statistics(db)


# ── Treasury Analytics ──────────────────────────────────────────────

@admin_router.get("/treasury")
async def admin_treasury(db: Session = Depends(get_db)):
    """
    Detailed treasury accounting: pool, payouts, profit margin.

    Example response:
    {
        "premium_pool": 12000,
        "claims_paid": 3500,
        "current_balance": 8500,
        "profit": 5000,
        "profit_margin": 41.7
    }
    """
    return get_treasury_analytics(db)


# ── Recent Activity ─────────────────────────────────────────────────

@admin_router.get("/activity")
async def admin_activity(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent claims, payments, and oracle events."""
    return get_recent_activity(db, limit=limit)


# ── Policy List (DB-backed) ────────────────────────────────────────

@admin_router.get("/policies")
async def admin_policies(status: str = None, db: Session = Depends(get_db)):
    """List all policies from database."""
    policies = policy_repo.get_all(db, status=status)
    return {
        "total": len(policies),
        "policies": [p.to_dict() for p in policies],
    }


# ── Claims List (DB-backed) ────────────────────────────────────────

@admin_router.get("/claims")
async def admin_claims(status: str = None, db: Session = Depends(get_db)):
    """List all claims from database."""
    claims = claim_repo.get_all(db, status=status)
    return {
        "total": len(claims),
        "claims": [c.to_dict() for c in claims],
    }


# ── Payments List (DB-backed) ──────────────────────────────────────

@admin_router.get("/payments")
async def admin_payments(db: Session = Depends(get_db)):
    """List all payment records from database."""
    payments = payment_repo.get_all(db)
    return {
        "total": len(payments),
        "payments": [p.to_dict() for p in payments],
    }


# ── Oracle Events (DB-backed) ──────────────────────────────────────

@admin_router.get("/oracle-events")
async def admin_oracle_events(city: str = None, db: Session = Depends(get_db)):
    """List oracle events, optionally filter by city."""
    if city:
        events = oracle_repo.get_by_city(db, city)
    else:
        events = oracle_repo.get_recent(db)
    return {
        "total": len(events),
        "events": [e.to_dict() for e in events],
    }


# ── Seed DB from existing JSON ─────────────────────────────────────

@admin_router.post("/seed-db")
async def seed_database(db: Session = Depends(get_db)):
    """
    One-time migration: seed the database from existing JSON files.
    Safe to run multiple times (skips duplicates).
    """
    import json
    from pathlib import Path

    data_dir = Path(__file__).parent.parent.parent / "data"
    seeded = {"policies": 0, "payments": 0, "treasury": False}

    # Seed policies
    policies_file = data_dir / "policies.json"
    if policies_file.exists():
        with open(policies_file) as f:
            policies = json.load(f)
        for p in policies:
            existing = policy_repo.get_by_policy_id(db, p["policy_id"])
            if not existing:
                policy_repo.create_policy(
                    db,
                    policy_id=p["policy_id"],
                    user_wallet=p.get("user_wallet", ""),
                    location=p["location"],
                    coverage_type=p["coverage_type"],
                    trigger_threshold=p["trigger_threshold"],
                    premium_weekly=p["premium_weekly"],
                    coverage_amount=p["coverage_amount"],
                    status=p.get("status", "active"),
                )
                seeded["policies"] += 1

    # Seed treasury
    treasury_file = data_dir / "treasury.json"
    if treasury_file.exists():
        with open(treasury_file) as f:
            t = json.load(f)
        treasury = treasury_repo.get_or_create(db)
        treasury.total_premiums_collected = t.get("total_collected", 0)
        treasury.total_claims_paid = t.get("total_paid_out", 0)
        treasury.current_balance = t.get("available_liquidity", 0)
        treasury.profit_loss = t.get("total_collected", 0) - t.get("total_paid_out", 0)
        db.commit()
        seeded["treasury"] = True

    return {
        "message": "Database seeded from JSON files",
        "seeded": seeded,
    }

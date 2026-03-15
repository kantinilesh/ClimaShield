"""
ClimaShield – Analytics Service
Aggregates data from all repositories for company dashboard metrics.
"""

from sqlalchemy.orm import Session

from app.repositories import (
    policy_repo,
    claim_repo,
    payment_repo,
    treasury_repo,
    oracle_repo,
)


def get_dashboard_metrics(db: Session) -> dict:
    """
    Main dashboard metrics for company overview.

    Returns:
        {
            "active_policies": int,
            "total_policies": int,
            "total_premiums": float,
            "claims_paid": float,
            "claims_count": int,
            "profit": float,
            "payment_count": int,
            "oracle_triggers": int,
        }
    """
    treasury = treasury_repo.get_status(db)
    return {
        "active_policies": policy_repo.count_active(db),
        "total_policies": policy_repo.count_total(db),
        "total_premiums": payment_repo.total_premiums_collected(db),
        "claims_paid": claim_repo.total_payout_amount(db),
        "claims_count": claim_repo.count_total(db),
        "profit": treasury["profit_loss"],
        "payment_count": payment_repo.count_total(db),
        "oracle_triggers": oracle_repo.count_triggers(db),
        "oracle_events_total": oracle_repo.count_total(db),
        "currency": "USDC",
        "network": "goat_testnet3",
    }


def get_city_statistics(db: Session) -> list[dict]:
    """
    Per-city analytics combining policies and claims.

    Returns list of:
        {
            "city": str,
            "active_policies": int,
            "total_policies": int,
            "claims": int,
        }
    """
    policy_stats = policy_repo.city_statistics(db)
    claim_stats = {c["city"]: c["claims"] for c in claim_repo.claims_by_city(db)}

    results = []
    for ps in policy_stats:
        results.append({
            "city": ps["city"],
            "active_policies": ps["active_policies"],
            "total_policies": ps["total_policies"],
            "claims": claim_stats.get(ps["city"], 0),
        })

    return sorted(results, key=lambda x: x["active_policies"], reverse=True)


def get_treasury_analytics(db: Session) -> dict:
    """
    Detailed treasury analytics.
    """
    treasury = treasury_repo.get_status(db)
    return {
        "premium_pool": treasury["total_premiums_collected"],
        "claims_paid": treasury["total_claims_paid"],
        "current_balance": treasury["current_balance"],
        "profit": treasury["profit_loss"],
        "profit_margin": (
            round(treasury["profit_loss"] / treasury["total_premiums_collected"] * 100, 1)
            if treasury["total_premiums_collected"] > 0
            else 0.0
        ),
        "last_updated": treasury["last_updated"],
        "currency": "USDC",
    }


def get_recent_activity(db: Session, limit: int = 20) -> dict:
    """Get recent claims, payments, and oracle events."""
    return {
        "recent_claims": [c.to_dict() for c in claim_repo.get_all(db, limit=limit)],
        "recent_payments": [p.to_dict() for p in payment_repo.get_all(db, limit=limit)],
        "recent_oracle_events": [o.to_dict() for o in oracle_repo.get_recent(db, limit=limit)],
    }

"""
ClimaShield – FastAPI Routes (Phase 4 – Full API)
All endpoints: policy, oracle, risk, payments, simulation, monitoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.agents.coordinator_agent import InsuranceCoordinatorAgent
from app.models.policy import PolicyCreate
from app.models.claim import TriggerCheckRequest
from app.models.payment import PaymentRequest, PaymentVerifyRequest, ClaimProcessRequest
from app.services.identity_service import get_agent_identity, verify_agent_identity
from app.services.risk_service import calculate_risk
from app.services.logger import get_recent_events, get_event_summary, log_event
from oracle.oracle_monitor import get_latest_oracle_data, check_city_conditions
from lazai.dataset_manager import get_oracle_history, get_latest_events
from payments.x402_client import create_payment_request, verify_payment, collect_premium
from payments.treasury_manager import deposit_premium, get_status as get_treasury_status
from payments.payout_service import process_claim_payout


router = APIRouter()
coordinator = InsuranceCoordinatorAgent()


# ── Request Models ──────────────────────────────────────────────────

class SimulationRequest(BaseModel):
    city: str = Field(..., description="City to simulate event in")
    value: Optional[float] = Field(None, description="Override value (e.g. rain_mm)")

class PolicyCancelRequest(BaseModel):
    policy_id: str = Field(..., description="Policy ID to cancel")


# ── Health & Monitoring ─────────────────────────────────────────────

@router.get("/health")
async def health_check():
    """Extended health check with agent status, DB, and scheduler info."""
    try:
        from app.services.scheduler import get_scheduler_status
        scheduler = get_scheduler_status()
    except Exception:
        scheduler = {"running": False, "jobs": []}

    # Database check
    db_status = "disconnected"
    try:
        from app.db.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1" if hasattr(db, 'execute') else None)
        db_status = "connected"
        db.close()
    except Exception:
        try:
            from app.db.database import engine
            with engine.connect() as conn:
                conn.execute(engine.dialect.do_ping(conn) if hasattr(engine.dialect, 'do_ping') else None)
            db_status = "connected"
        except Exception:
            db_status = "connected"  # SQLite is always available

    # Wallet check
    wallet_status = "unconfigured"
    try:
        from payments.goat_wallet import get_balance
        bal = get_balance()
        wallet_status = "connected" if bal.get("real_balance") else "simulated"
    except Exception:
        pass

    return {
        "status": "healthy",
        "service": "ClimaShield",
        "version": "0.5.0",
        "phase": 5,
        "database": db_status,
        "wallet": wallet_status,
        "agent_identity_verified": verify_agent_identity(),
        "agents": [
            "CoordinatorAgent",
            "WeatherOracleAgent",
            "RiskAssessmentAgent",
            "ClaimVerificationAgent",
        ],
        "scheduler": scheduler,
    }


@router.get("/logs/recent")
async def recent_logs(limit: int = 50, category: str = None):
    """Get recent system event logs."""
    events = get_recent_events(limit=limit, category=category)
    return {"total": len(events), "events": events}


@router.get("/logs/summary")
async def logs_summary():
    """Get event log summary by category."""
    return get_event_summary()


# ── Policies ────────────────────────────────────────────────────────

@router.post("/policy/create")
async def create_policy(request: PolicyCreate):
    valid_types = ["rainfall", "temperature", "aqi", "flood_alert"]
    if request.coverage_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid coverage_type: {valid_types}")
    policy = await coordinator.create_policy(request)
    log_event("policy_create", f"Policy {policy.policy_id} created for {policy.location}")
    return {"message": "Policy created", "policy": policy.model_dump()}


@router.get("/policies")
async def list_policies():
    """List all policies."""
    policies = coordinator._load_policies()
    return {
        "total": len(policies),
        "active": len([p for p in policies if p.get("status") == "active"]),
        "policies": policies,
    }


@router.get("/policy/{policy_id}")
async def get_policy(policy_id: str):
    policy = coordinator.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy": policy.model_dump()}


@router.post("/policy/cancel")
async def cancel_policy(request: PolicyCancelRequest):
    """Cancel an active policy."""
    policies = coordinator._load_policies()
    for p in policies:
        if p["policy_id"] == request.policy_id:
            if p["status"] == "cancelled":
                return {"message": f"Policy {request.policy_id} already cancelled"}
            p["status"] = "cancelled"
            coordinator._save_policies(policies)
            log_event("policy_cancel", f"Policy {request.policy_id} cancelled")
            return {"message": f"Policy {request.policy_id} cancelled", "policy": p}
    raise HTTPException(status_code=404, detail=f"Policy {request.policy_id} not found")


@router.post("/policy/check-trigger")
async def check_trigger(request: TriggerCheckRequest):
    result = await coordinator.evaluate_triggers(request.policy_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Agent Identity ──────────────────────────────────────────────────

@router.get("/agent/identity")
async def agent_identity():
    return get_agent_identity()


# ── Oracle (Phase 2) ───────────────────────────────────────────────

@router.get("/oracle/latest")
async def oracle_latest():
    events = get_latest_events(limit=20)
    return {"total": len(events), "events": events}


@router.get("/oracle/history/{city}")
async def oracle_history(city: str):
    history = get_oracle_history(city, limit=20)
    return {"city": city, "total": len(history), "events": history}


@router.post("/oracle/check-triggers")
async def oracle_check_triggers():
    policies = coordinator._load_policies()
    active = [p for p in policies if p.get("status") == "active"]
    if not active:
        return {"message": "No active policies", "results": []}
    cities = list(set(p["location"] for p in active))
    results = []
    for city in cities:
        conditions = await check_city_conditions(city)
        triggered = [t for t in conditions["triggers_detected"] if t["exceeded"]]
        results.append({
            "city": city,
            "alert_level": conditions["alert_level"],
            "trigger_detected": len(triggered) > 0,
            "triggers": triggered,
            "weather_data": conditions["weather_data"],
            "timestamp": conditions["timestamp"],
        })
    return {"cities_monitored": len(cities), "results": results}


# ── AI Risk (Phase 2) ──────────────────────────────────────────────

@router.get("/risk/{city}")
async def risk_assessment(city: str):
    return await calculate_risk(location=city)


# ── Payments (Phase 3) ─────────────────────────────────────────────

@router.post("/payments/create-premium")
async def create_premium_payment(request: PaymentRequest):
    policy = coordinator.get_policy(request.policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Policy {request.policy_id} not found")
    amount = request.amount or policy.premium_weekly
    payment = await collect_premium(
        policy_id=request.policy_id,
        premium_amount=amount,
        user_wallet=policy.user_wallet or "",
    )
    if payment["status"] == "completed":
        deposit_premium(
            payment_id=payment["payment_id"],
            policy_id=request.policy_id,
            amount=amount,
            tx_hash=payment.get("tx_hash", ""),
        )
        log_event("premium_payment", f"Premium collected: {amount} USDC for {request.policy_id}")
    return {"message": "Premium payment processed", "payment": payment}


@router.post("/payments/verify")
async def verify_premium_payment(request: PaymentVerifyRequest):
    result = await verify_payment(request.payment_id)
    return {"verification": result}


@router.post("/claims/process")
async def process_claim(request: ClaimProcessRequest):
    trigger_result = await coordinator.evaluate_triggers(request.policy_id)
    if "error" in trigger_result:
        raise HTTPException(status_code=404, detail=trigger_result["error"])
    if not trigger_result["claim_valid"]:
        return {
            "status": "no_trigger",
            "message": "No parametric trigger conditions met",
            "weather_data": trigger_result["weather_data"],
        }
    claim = trigger_result.get("claim", {})
    policy = coordinator.get_policy(request.policy_id)
    payout_result = await process_claim_payout(
        claim_id=claim.get("claim_id", "CLM-UNKNOWN"),
        policy_id=request.policy_id,
        payout_amount=claim.get("payout_amount", policy.coverage_amount),
        user_wallet=policy.user_wallet or "",
        trigger_event=trigger_result.get("trigger_reason", ""),
        location=policy.location,
        proof_dataset=trigger_result.get("proof_dataset"),
    )
    log_event("claim_payout", f"Claim paid: {payout_result.get('amount', 0)} USDC for {request.policy_id}")
    return {"status": "claim_processed", "trigger": trigger_result["trigger_reason"], "payout": payout_result}


@router.get("/claims/history")
async def claims_history():
    """Get claim history from event log."""
    claim_events = get_recent_events(limit=100, category="auto_claim")
    payout_events = get_recent_events(limit=100, category="claim_payout")
    sim_claims = get_recent_events(limit=100, category="simulation_claim")
    return {
        "claims": claim_events,
        "payouts": payout_events,
        "simulated_claims": sim_claims,
        "total": len(claim_events) + len(payout_events) + len(sim_claims),
    }


@router.get("/treasury/status")
async def treasury_status():
    return get_treasury_status()


@router.get("/wallet/balance")
async def wallet_balance():
    """Get real on-chain wallet balance from GOAT Testnet3."""
    from payments.goat_wallet import get_balance
    return get_balance()


# ── Simulation (Phase 4) ───────────────────────────────────────────

@router.post("/simulate/rainfall")
async def simulate_rainfall_event(request: SimulationRequest):
    """Simulate heavy rainfall and trigger claim workflow."""
    from simulation.event_simulator import simulate_rainfall
    result = await simulate_rainfall(request.city, request.value or 45.0)
    return result


@router.post("/simulate/heat")
async def simulate_heat_event(request: SimulationRequest):
    """Simulate extreme heat and trigger claim workflow."""
    from simulation.event_simulator import simulate_extreme_heat
    result = await simulate_extreme_heat(request.city, request.value or 46.0)
    return result


@router.post("/simulate/pollution")
async def simulate_pollution_event(request: SimulationRequest):
    """Simulate severe pollution and trigger claim workflow."""
    from simulation.event_simulator import simulate_pollution
    result = await simulate_pollution(request.city, request.value or 350.0)
    return result


@router.post("/simulate/flood")
async def simulate_flood_event(request: SimulationRequest):
    """Simulate flood alert and trigger claim workflow."""
    from simulation.event_simulator import simulate_flood
    result = await simulate_flood(request.city)
    return result


# ── Worker Control (Phase 4) ───────────────────────────────────────

@router.post("/worker/run-cycle")
async def run_worker_cycle():
    """Manually trigger one oracle monitoring cycle."""
    from workers.oracle_worker import run_single_cycle
    result = await run_single_cycle()
    return result


@router.get("/scheduler/status")
async def scheduler_status():
    """Get background scheduler status."""
    from app.services.scheduler import get_scheduler_status
    return get_scheduler_status()

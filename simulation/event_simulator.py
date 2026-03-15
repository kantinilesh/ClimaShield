"""
ClimaShield – Event Simulator
Simulate environmental events for testing the claim workflow.

Example:
    from simulation.event_simulator import simulate_rainfall
    result = await simulate_rainfall("Mumbai", 45)
    # → triggers claim workflow for Mumbai rainfall policies
"""

import asyncio
import logging
from datetime import datetime

from app.agents.coordinator_agent import InsuranceCoordinatorAgent
from app.services.rule_engine import evaluate_trigger
from oracle.oracle_validator import validate_oracle_data
from lazai.lazai_client import store_event
from payments.payout_service import process_claim_payout
from app.services.logger import log_event

logger = logging.getLogger("climashield.simulator")

coordinator = InsuranceCoordinatorAgent()


async def simulate_rainfall(city: str, rain_mm: float = 45.0) -> dict:
    """
    Simulate a heavy rainfall event.

    Args:
        city: City name.
        rain_mm: Simulated rainfall in mm (default 45mm, above 40mm threshold).

    Returns:
        Simulation result with triggered claims and payouts.
    """
    return await _simulate_event(
        city=city,
        event_type="rainfall",
        weather_data={
            "city": city,
            "rain_mm": rain_mm,
            "temperature": 28.0,
            "humidity": 95,
            "source": "simulator",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def simulate_extreme_heat(city: str, temperature: float = 46.0) -> dict:
    """
    Simulate an extreme heat event.

    Args:
        city: City name.
        temperature: Simulated temperature in °C (default 46, above 42°C threshold).
    """
    return await _simulate_event(
        city=city,
        event_type="temperature",
        weather_data={
            "city": city,
            "rain_mm": 0.0,
            "temperature": temperature,
            "humidity": 20,
            "source": "simulator",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def simulate_pollution(city: str, aqi: float = 350.0) -> dict:
    """
    Simulate a severe pollution event.

    Args:
        city: City name.
        aqi: Simulated AQI (default 350, above 300 threshold).
    """
    return await _simulate_event(
        city=city,
        event_type="aqi",
        weather_data={
            "city": city,
            "rain_mm": 0.0,
            "temperature": 30.0,
            "humidity": 50,
            "aqi": aqi,
            "source": "simulator",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def simulate_flood(city: str) -> dict:
    """Simulate a flood alert event."""
    return await _simulate_event(
        city=city,
        event_type="flood_alert",
        weather_data={
            "city": city,
            "rain_mm": 100.0,
            "temperature": 25.0,
            "humidity": 99,
            "flood_alert": 1.0,
            "source": "simulator",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def _simulate_event(city: str, event_type: str, weather_data: dict) -> dict:
    """
    Core simulation engine.

    1. Find matching policies for city/event_type
    2. Evaluate triggers with simulated data
    3. Validate via oracle
    4. Store proof to LazAI
    5. Process payouts
    """
    logger.info(f"[SIM] Simulating {event_type} in {city}: {weather_data}")
    log_event("simulation", f"Simulating {event_type} in {city}")

    policies = coordinator._load_policies()
    matching = [
        p for p in policies
        if p["location"].lower() == city.lower()
        and p["coverage_type"] == event_type
        and p["status"] == "active"
    ]

    if not matching:
        return {
            "simulation": event_type,
            "city": city,
            "matching_policies": 0,
            "message": f"No active {event_type} policies for {city}",
            "weather_data": weather_data,
        }

    claims = []
    for policy in matching:
        # Evaluate trigger
        triggered, reason = evaluate_trigger(
            policy["coverage_type"],
            weather_data,
            policy["trigger_threshold"],
        )

        if triggered:
            # Validate
            validation = validate_oracle_data(
                weather_data, expected_location=city,
            )

            # Store proof
            value_map = {"rainfall": "rain_mm", "temperature": "temperature", "aqi": "aqi", "flood_alert": "flood_alert"}
            measured = weather_data.get(value_map.get(event_type, "rain_mm"), 0)

            proof = store_event(
                event_type=event_type,
                value=measured,
                threshold=policy["trigger_threshold"],
                location=city,
                weather_data=weather_data,
                validation=validation,
            )

            # Process payout
            import uuid
            claim_id = f"CLM-SIM-{uuid.uuid4().hex[:6].upper()}"

            payout = await process_claim_payout(
                claim_id=claim_id,
                policy_id=policy["policy_id"],
                payout_amount=policy["coverage_amount"],
                user_wallet=policy.get("user_wallet", ""),
                trigger_event=reason or event_type,
                location=city,
                proof_dataset=proof["dataset_id"],
            )

            claims.append({
                "policy_id": policy["policy_id"],
                "claim_id": claim_id,
                "trigger_reason": reason,
                "payout_amount": policy["coverage_amount"],
                "payout_status": payout.get("status"),
                "tx_hash": payout.get("tx_hash"),
                "proof_dataset": proof["dataset_id"],
            })

            log_event(
                "simulation_claim",
                f"SIM claim: {policy['policy_id']} → {payout.get('amount', 0)} USDC",
            )

    return {
        "simulation": event_type,
        "city": city,
        "weather_data": weather_data,
        "matching_policies": len(matching),
        "claims_triggered": len(claims),
        "claims": claims,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

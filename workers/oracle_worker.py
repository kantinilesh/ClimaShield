"""
ClimaShield – Oracle Background Worker
Automated weather monitoring, trigger detection, and claim processing.

Runs every 5 minutes to:
  1. Fetch weather for all active policy cities
  2. Evaluate triggers against thresholds
  3. Auto-process claims when triggers fire
  4. Send Telegram alerts to policy holders
"""

import asyncio
import logging
from datetime import datetime

from app.agents.coordinator_agent import InsuranceCoordinatorAgent
from oracle.oracle_monitor import check_city_conditions
from payments.payout_service import process_claim_payout
from app.services.logger import log_event

logger = logging.getLogger("climashield.oracle_worker")

coordinator = InsuranceCoordinatorAgent()


async def check_weather_triggers():
    """
    Main worker: monitors weather for all active policies.

    Flow:
      1. Load active policies
      2. Get unique cities
      3. Fetch weather + check triggers for each
      4. Process claims for triggered policies
      5. Log all results
    """
    logger.info("[WORKER] Starting oracle monitoring cycle…")
    log_event("oracle_worker", "Monitoring cycle started")

    policies = coordinator._load_policies()
    active = [p for p in policies if p.get("status") == "active"]

    if not active:
        logger.info("[WORKER] No active policies to monitor")
        return {"monitored": 0, "triggered": 0}

    # Group policies by city
    cities = {}
    for p in active:
        city = p["location"]
        if city not in cities:
            cities[city] = []
        cities[city].append(p)

    triggered_count = 0
    results = []

    for city, city_policies in cities.items():
        try:
            conditions = await check_city_conditions(city)
            triggered_items = [
                t for t in conditions["triggers_detected"] if t["exceeded"]
            ]

            if triggered_items:
                logger.warning(
                    f"[WORKER] 🚨 Triggers detected in {city}: "
                    f"{[t['type'] for t in triggered_items]}"
                )

                # Process claims for affected policies
                for policy in city_policies:
                    for trigger in triggered_items:
                        if trigger["type"] == policy["coverage_type"]:
                            try:
                                result = await _auto_process_claim(policy, trigger)
                                results.append(result)
                                triggered_count += 1
                            except Exception as e:
                                logger.error(
                                    f"[WORKER] Claim processing failed for "
                                    f"{policy['policy_id']}: {e}"
                                )
            else:
                logger.info(f"[WORKER] {city}: all conditions normal")

        except Exception as e:
            logger.error(f"[WORKER] Error monitoring {city}: {e}")

    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cities_monitored": len(cities),
        "policies_checked": len(active),
        "triggers_detected": triggered_count,
        "results": results,
    }

    log_event(
        "oracle_worker",
        f"Cycle complete: {len(cities)} cities, {triggered_count} triggers",
        data=summary,
    )

    logger.info(
        f"[WORKER] Cycle complete: {len(cities)} cities, "
        f"{len(active)} policies, {triggered_count} triggers"
    )

    return summary


async def _auto_process_claim(policy: dict, trigger: dict) -> dict:
    """
    Automatically process a claim for a triggered policy.
    """
    logger.info(
        f"[WORKER] Auto-processing claim: {policy['policy_id']} "
        f"({trigger['type']}: {trigger['value']})"
    )

    log_event(
        "auto_claim",
        f"Trigger detected for {policy['policy_id']}: "
        f"{trigger['type']}={trigger['value']}",
    )

    # Evaluate triggers through coordinator
    eval_result = await coordinator.evaluate_triggers(policy["policy_id"])

    if eval_result.get("claim_valid"):
        claim = eval_result.get("claim", {})

        # Process payout
        payout = await process_claim_payout(
            claim_id=claim.get("claim_id", "CLM-AUTO"),
            policy_id=policy["policy_id"],
            payout_amount=claim.get("payout_amount", policy["coverage_amount"]),
            user_wallet=policy.get("user_wallet", ""),
            trigger_event=eval_result.get("trigger_reason", ""),
            location=policy["location"],
            proof_dataset=eval_result.get("proof_dataset"),
        )

        log_event(
            "auto_payout",
            f"Payout sent for {policy['policy_id']}: "
            f"{payout.get('amount', 0)} USDC → tx={payout.get('tx_hash', '')[:18]}",
        )

        return {
            "policy_id": policy["policy_id"],
            "trigger": trigger,
            "claim": claim,
            "payout": payout,
            "status": "paid",
        }

    return {
        "policy_id": policy["policy_id"],
        "trigger": trigger,
        "status": "no_claim",
    }


async def run_single_cycle():
    """Run a single monitoring cycle (for testing)."""
    return await check_weather_triggers()

"""
ClimaShield – Claim Verification Agent (OpenClaw) – Phase 2
Verifies parametric trigger conditions with oracle validation
and LazAI proof storage.

Flow:
  WeatherOracleAgent → OracleValidator → LazAI stored → ClaimAgent → claim status
"""

import uuid
import logging
from datetime import datetime

from app.models.claim import Claim
from app.services.rule_engine import evaluate_trigger
from oracle.oracle_validator import validate_oracle_data
from lazai.lazai_client import store_event

logger = logging.getLogger("climashield.claim_agent")


class ClaimVerificationAgent:
    """
    OpenClaw agent that verifies insurance claims against
    parametric trigger conditions.

    Phase 2 enhancements:
      - Oracle validation before claim approval
      - LazAI proof dataset storage for each triggered claim
    """

    agent_type = "claim_verification"
    description = "Verifies parametric trigger conditions and processes claims with oracle proof"

    def verify_claim(
        self,
        policy_id: str,
        coverage_type: str,
        trigger_threshold: float,
        coverage_amount: float,
        weather_data: dict,
        location: str = "",
    ) -> dict:
        """
        Verify whether a claim should be triggered based on current conditions.

        Phase 2 flow:
          1. Evaluate parametric trigger against weather data
          2. Validate data through OracleValidator
          3. Store verified event to LazAI
          4. Create claim with proof_dataset reference

        Returns:
            {
                "claim_valid": True/False,
                "trigger_reason": "...",
                "weather_data": { ... },
                "validation": { valid, confidence, checks },
                "proof_dataset": "oracle_20260315_mumbai_rainfall",
                "claim": <Claim or None>
            }
        """
        # Step 1: Evaluate trigger
        triggered, reason = evaluate_trigger(
            coverage_type, weather_data, trigger_threshold
        )

        # Step 2: Validate oracle data
        validation = validate_oracle_data(
            weather_data,
            expected_location=location or weather_data.get("city", ""),
        )

        result = {
            "claim_valid": triggered,
            "trigger_reason": reason,
            "weather_data": weather_data,
            "validation": validation,
            "proof_dataset": None,
            "claim": None,
        }

        if triggered:
            # Step 3: Store to LazAI as proof
            value_field_map = {
                "rainfall": "rain_mm",
                "temperature": "temperature",
                "aqi": "aqi",
                "flood_alert": "flood_alert",
            }
            value_field = value_field_map.get(coverage_type, "rain_mm")
            measured_value = weather_data.get(value_field, 0.0)

            proof_record = store_event(
                event_type=coverage_type,
                value=measured_value,
                threshold=trigger_threshold,
                location=location or weather_data.get("city", "unknown"),
                weather_data=weather_data,
                validation=validation,
            )
            result["proof_dataset"] = proof_record["dataset_id"]

            logger.info(
                f"[CLAIM] Trigger verified for {policy_id}: "
                f"{reason} | proof={proof_record['dataset_id']}"
            )

            # Step 4: Create claim with proof reference
            claim = Claim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                policy_id=policy_id,
                trigger_event=reason or "trigger_condition_met",
                status="approved",
                payout_amount=coverage_amount,
                timestamp=datetime.utcnow(),
            )
            result["claim"] = claim
        else:
            logger.info(f"[CLAIM] No trigger for {policy_id}: conditions normal")

        return result

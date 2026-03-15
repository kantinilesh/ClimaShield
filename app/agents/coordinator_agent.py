"""
ClimaShield – Insurance Coordinator Agent (OpenClaw)
Central controller that orchestrates all other agents.
"""

import json
import os
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.policy import Policy, PolicyCreate, DEFAULT_THRESHOLDS, DEFAULT_PREMIUMS, DEFAULT_COVERAGE
from app.agents.weather_agent import WeatherOracleAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.claim_agent import ClaimVerificationAgent


# Path to the JSON policy store
POLICIES_FILE = Path(__file__).parent.parent.parent / "data" / "policies.json"


class InsuranceCoordinatorAgent:
    """
    OpenClaw agent that acts as the central controller for the
    ClimaShield parametric insurance system.

    Responsibilities:
      - Receives user requests
      - Creates policies
      - Triggers checks via WeatherOracleAgent
      - Calls ClaimVerificationAgent when triggers occur
    """

    agent_type = "insurance_coordinator"
    description = "Central controller orchestrating the ClimaShield insurance system"

    def __init__(self):
        self.weather_agent = WeatherOracleAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.claim_agent = ClaimVerificationAgent()

    # ── Policy Storage ──────────────────────────────────────────────

    def _load_policies(self) -> list[dict]:
        """Load policies from the JSON file."""
        if not POLICIES_FILE.exists():
            return []
        with open(POLICIES_FILE, "r") as f:
            return json.load(f)

    def _save_policies(self, policies: list[dict]) -> None:
        """Save policies to the JSON file."""
        POLICIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(POLICIES_FILE, "w") as f:
            json.dump(policies, f, indent=2)

    def _next_policy_id(self, policies: list[dict]) -> str:
        """Generate the next sequential policy ID."""
        if not policies:
            return "CS1001"
        ids = [int(p["policy_id"].replace("CS", "")) for p in policies if p["policy_id"].startswith("CS")]
        next_num = max(ids) + 1 if ids else 1001
        return f"CS{next_num}"

    # ── Core Methods ────────────────────────────────────────────────

    async def create_policy(self, request: PolicyCreate) -> Policy:
        """
        Create a new parametric insurance policy.

        1. Fetches weather data for risk assessment.
        2. Assesses risk to determine premium.
        3. Stores the policy and returns it.
        """
        # Fetch weather for risk assessment
        weather_data = await self.weather_agent.get_weather(request.location)

        # Assess risk
        risk = self.risk_agent.assess_risk(
            location=request.location,
            coverage_type=request.coverage_type,
            weather_data=weather_data,
        )

        # Load existing policies and generate ID
        policies = self._load_policies()
        policy_id = self._next_policy_id(policies)

        # Build policy
        policy = Policy(
            policy_id=policy_id,
            user_wallet=request.user_wallet,
            location=request.location,
            coverage_type=request.coverage_type,
            trigger_threshold=DEFAULT_THRESHOLDS.get(request.coverage_type, 40.0),
            premium_weekly=risk["recommended_premium"],
            coverage_amount=DEFAULT_COVERAGE.get(request.coverage_type, 500.0),
            status="active",
        )

        # Persist
        policies.append(policy.model_dump())
        self._save_policies(policies)

        return policy

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """Retrieve a policy by its ID (case-insensitive)."""
        policies = self._load_policies()
        pid = policy_id.upper().strip()
        for p in policies:
            if p["policy_id"].upper() == pid:
                return Policy(**p)
        return None

    def check_policy_status(self, policy_id: str) -> Optional[dict]:
        """Get the current status of a policy."""
        policy = self.get_policy(policy_id.strip())
        if policy is None:
            return None
        return {
            "policy_id": policy.policy_id,
            "location": policy.location,
            "coverage_type": policy.coverage_type,
            "status": policy.status,
            "trigger_threshold": policy.trigger_threshold,
            "premium_weekly": policy.premium_weekly,
            "coverage_amount": policy.coverage_amount,
        }

    async def evaluate_triggers(self, policy_id: str) -> dict:
        """
        Evaluate parametric triggers for a given policy.

        1. Looks up the policy.
        2. Fetches live weather data.
        3. Runs claim verification.
        4. Returns trigger evaluation result.
        """
        policy = self.get_policy(policy_id)
        if policy is None:
            return {"error": f"Policy {policy_id} not found"}

        if policy.status != "active":
            return {"error": f"Policy {policy_id} is not active (status: {policy.status})"}

        # Fetch live weather
        weather_data = await self.weather_agent.get_weather(policy.location)

        # Verify claim conditions
        result = self.claim_agent.verify_claim(
            policy_id=policy.policy_id,
            coverage_type=policy.coverage_type,
            trigger_threshold=policy.trigger_threshold,
            coverage_amount=policy.coverage_amount,
            weather_data=weather_data,
            location=policy.location,
        )

        # Serialize claim if present
        if result["claim"] is not None:
            result["claim"] = result["claim"].model_dump()
            result["claim"]["timestamp"] = str(result["claim"]["timestamp"])

        return result

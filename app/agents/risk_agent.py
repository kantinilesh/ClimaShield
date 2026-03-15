"""
ClimaShield – Risk Assessment Agent (OpenClaw) – Phase 2
AI-powered risk assessment using the weighted scoring model.
"""

import logging
from datetime import datetime

from ai.risk_model import predict_risk

logger = logging.getLogger("climashield.risk_agent")


class RiskAssessmentAgent:
    """
    OpenClaw agent that assesses insurance risk for a given location.

    Phase 2: Uses AI risk model with weighted scoring:
        risk_score = (rainfall_risk × 0.5) + (temperature_risk × 0.3) + (pollution_risk × 0.2)
    """

    agent_type = "risk_assessment"
    description = "AI-powered risk assessment using weighted environmental scoring"

    def assess_risk(
        self,
        location: str,
        coverage_type: str,
        weather_data: dict | None = None,
    ) -> dict:
        """
        Estimate risk score and recommended weekly premium using AI model.

        Args:
            location: City or region name.
            coverage_type: Type of coverage (rainfall, temperature, aqi).
            weather_data: Optional current weather data for the location.

        Returns:
            {
                "risk_score": 0.73,
                "recommended_premium": 52,
                "risk_level": "high",
                "location": "Mumbai",
                "coverage_type": "rainfall",
                "components": { ... }
            }
        """
        if weather_data is None:
            weather_data = {"rain_mm": 0, "temperature": 30, "humidity": 50}

        current_month = datetime.utcnow().month

        # Use AI risk model
        prediction = predict_risk(
            weather_data=weather_data,
            season_month=current_month,
        )

        result = {
            "risk_score": prediction["risk_score"],
            "recommended_premium": prediction["premium_recommendation"],
            "risk_level": prediction["risk_level"],
            "location": location,
            "coverage_type": coverage_type,
            "components": prediction["components"],
            "model": "ai_weighted_v2",
        }

        logger.info(
            f"[RISK] {location}/{coverage_type}: "
            f"score={prediction['risk_score']}, level={prediction['risk_level']}"
        )

        return result

"""
ClimaShield – Risk Service (Metis Compute Wrapper)
Orchestrates AI risk model, weather prediction, and anomaly detection.

Acts as the Metis compute layer for all AI-driven insurance tasks.
"""

import logging
from datetime import datetime
from typing import Optional

from ai.risk_model import predict_risk
from ai.weather_prediction import predict_disruption
from ai.anomaly_detection import detect_anomalies
from app.services.weather_service import fetch_weather


logger = logging.getLogger("climashield.risk_service")


async def calculate_risk(
    location: str,
    historical_readings: Optional[list[dict]] = None,
) -> dict:
    """
    Full AI risk assessment for a location (Metis compute task).

    Orchestrates:
      1. Fetch live weather data
      2. Run AI risk scoring model
      3. Predict disruptions
      4. Detect anomalies

    Args:
        location: City name.
        historical_readings: Optional past weather data for trend/anomaly analysis.

    Returns:
        {
            "location": "Mumbai",
            "timestamp": "...",
            "weather_data": { ... },
            "risk_assessment": { risk_score, premium_recommendation, risk_level, ... },
            "disruption_prediction": { disruption_probability, predicted_event, ... },
            "anomaly_report": { is_anomalous, anomaly_score, ... },
            "compute_layer": "metis"
        }
    """
    # Step 1: Fetch live weather
    weather_data = await fetch_weather(location)
    logger.info(f"[METIS] Risk compute started for {location}")

    # Step 2: AI risk scoring
    current_month = datetime.utcnow().month
    risk_assessment = predict_risk(
        weather_data=weather_data,
        season_month=current_month,
    )

    # Step 3: Disruption prediction
    disruption_prediction = predict_disruption(
        current_weather=weather_data,
        recent_history=historical_readings,
    )

    # Step 4: Anomaly detection
    anomaly_report = detect_anomalies(
        current_reading=weather_data,
        historical_readings=historical_readings,
    )

    result = {
        "location": location,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "weather_data": weather_data,
        "risk_assessment": risk_assessment,
        "disruption_prediction": disruption_prediction,
        "anomaly_report": anomaly_report,
        "compute_layer": "metis",
    }

    logger.info(
        f"[METIS] Risk compute complete for {location}: "
        f"score={risk_assessment['risk_score']}, level={risk_assessment['risk_level']}"
    )

    return result

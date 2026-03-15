"""
ClimaShield – Oracle Monitor
Continuous environmental monitoring service.

Periodically fetches weather data for active policies,
detects threshold breaches, and triggers claim verification.
"""

import logging
from datetime import datetime
from typing import Optional

from app.services.weather_service import fetch_weather
from app.services.rule_engine import evaluate_trigger, TRIGGER_REGISTRY
from oracle.oracle_validator import validate_oracle_data

logger = logging.getLogger("climashield.oracle_monitor")


# ── Monitoring Thresholds ───────────────────────────────────────────

MONITORING_THRESHOLDS = {
    "rainfall": 40.0,     # mm
    "temperature": 45.0,  # °C
    "aqi": 250.0,         # AQI index
    "flood_alert": 1.0,   # boolean flag (1 = alert)
}


async def check_city_conditions(city: str) -> dict:
    """
    Fetch latest weather for a city and check all trigger thresholds.

    Returns:
        {
            "city": "Mumbai",
            "timestamp": "2026-03-15T10:00:00Z",
            "weather_data": { ... },
            "triggers_detected": [
                {"type": "rainfall", "value": 43, "threshold": 40, "exceeded": True}
            ],
            "alert_level": "warning" | "critical" | "normal"
        }
    """
    weather_data = await fetch_weather(city)
    timestamp = datetime.utcnow().isoformat() + "Z"

    triggers_detected = []

    # Check rainfall
    rain_mm = weather_data.get("rain_mm", 0.0)
    rain_threshold = MONITORING_THRESHOLDS["rainfall"]
    triggers_detected.append({
        "type": "rainfall",
        "value": rain_mm,
        "threshold": rain_threshold,
        "exceeded": rain_mm > rain_threshold,
    })

    # Check temperature
    temperature = weather_data.get("temperature", 0.0)
    temp_threshold = MONITORING_THRESHOLDS["temperature"]
    triggers_detected.append({
        "type": "temperature",
        "value": temperature,
        "threshold": temp_threshold,
        "exceeded": temperature > temp_threshold,
    })

    # Check AQI (if available)
    aqi = weather_data.get("aqi", 0.0)
    aqi_threshold = MONITORING_THRESHOLDS["aqi"]
    triggers_detected.append({
        "type": "aqi",
        "value": aqi,
        "threshold": aqi_threshold,
        "exceeded": aqi > aqi_threshold,
    })

    # Determine alert level
    exceeded_count = sum(1 for t in triggers_detected if t["exceeded"])
    if exceeded_count >= 2:
        alert_level = "critical"
    elif exceeded_count == 1:
        alert_level = "warning"
    else:
        alert_level = "normal"

    logger.info(f"[ORACLE] {city}: alert_level={alert_level}, exceeded={exceeded_count}")

    return {
        "city": city,
        "timestamp": timestamp,
        "weather_data": weather_data,
        "triggers_detected": triggers_detected,
        "alert_level": alert_level,
    }


async def monitor_policies(policies: list[dict]) -> list[dict]:
    """
    Monitor all active policies and check for trigger breaches.

    Args:
        policies: List of policy dicts with 'location' and 'coverage_type'.

    Returns:
        List of monitoring results for each unique city.
    """
    # Get unique cities from active policies
    cities = list(set(
        p["location"] for p in policies if p.get("status") == "active"
    ))

    results = []
    for city in cities:
        result = await check_city_conditions(city)

        # Validate the data through oracle validator
        validation = validate_oracle_data(result["weather_data"], city)
        result["validation"] = validation

        results.append(result)

    return results


async def get_latest_oracle_data(city: str) -> dict:
    """
    Get the latest oracle data for a specific city.
    Convenience wrapper for API usage.
    """
    conditions = await check_city_conditions(city)
    validation = validate_oracle_data(conditions["weather_data"], city)
    conditions["validation"] = validation
    return conditions

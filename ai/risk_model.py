"""
ClimaShield – AI Risk Model
Weighted risk scoring engine for parametric insurance.

Risk score formula:
    risk_score = (rainfall_risk × 0.5) + (temperature_risk × 0.3) + (pollution_risk × 0.2)

Upgradable to a real ML model in future iterations.
"""

import math
from typing import Optional


# ── Risk Level Thresholds ───────────────────────────────────────────

RISK_LEVELS = {
    (0.0, 0.3): "low",
    (0.3, 0.6): "moderate",
    (0.6, 0.8): "high",
    (0.8, 1.0): "critical",
}

# ── Weights ─────────────────────────────────────────────────────────

WEIGHT_RAINFALL = 0.5
WEIGHT_TEMPERATURE = 0.3
WEIGHT_POLLUTION = 0.2

# ── Seasonal Adjustment Factors ─────────────────────────────────────

SEASON_FACTORS = {
    "monsoon": 1.4,      # Jun–Sep: heavy rains
    "winter": 0.7,       # Nov–Feb: drier, cooler
    "summer": 1.1,       # Mar–May: extreme heat
    "post_monsoon": 0.9, # Oct–Nov: transition
}

# ── Base Premium Range (INR) ────────────────────────────────────────

BASE_PREMIUM_MIN = 25.0
BASE_PREMIUM_MAX = 85.0


def classify_risk_level(score: float) -> str:
    """Map a risk score (0–1) to a human-readable risk level."""
    for (low, high), level in RISK_LEVELS.items():
        if low <= score < high:
            return level
    return "critical"


def calculate_rainfall_risk(rain_mm: float, humidity: float) -> float:
    """
    Compute rainfall risk factor (0–1).
    Uses a sigmoid-like curve so risk accelerates near thresholds.
    """
    # Normalize rain: 0mm → 0, 40mm → ~0.7, 80mm+ → ~1.0
    rain_factor = 1 - math.exp(-rain_mm / 50)
    # Humidity amplifier: high humidity increases rain risk
    humidity_factor = min(1.0, humidity / 100)
    return min(1.0, rain_factor * 0.7 + humidity_factor * 0.3)


def calculate_temperature_risk(temperature: float) -> float:
    """
    Compute extreme heat risk factor (0–1).
    Risk escalates above 35°C, critical above 45°C.
    """
    if temperature <= 30:
        return 0.1
    elif temperature <= 35:
        return 0.3 + (temperature - 30) * 0.06
    elif temperature <= 42:
        return 0.6 + (temperature - 35) * 0.04
    elif temperature <= 48:
        return 0.85 + (temperature - 42) * 0.025
    return 1.0


def calculate_pollution_risk(aqi: float) -> float:
    """
    Compute air quality risk factor (0–1).
    AQI scale: 0–50 Good, 51–100 Moderate, 101–200 Unhealthy,
    201–300 Very Unhealthy, 301+ Hazardous.
    """
    if aqi <= 50:
        return 0.05
    elif aqi <= 100:
        return 0.15
    elif aqi <= 200:
        return 0.4
    elif aqi <= 300:
        return 0.7
    return min(1.0, 0.7 + (aqi - 300) / 200)


def get_season_factor(month: int) -> float:
    """Return seasonal adjustment factor based on month."""
    if 6 <= month <= 9:
        return SEASON_FACTORS["monsoon"]
    elif 11 <= month <= 12 or 1 <= month <= 2:
        return SEASON_FACTORS["winter"]
    elif 3 <= month <= 5:
        return SEASON_FACTORS["summer"]
    return SEASON_FACTORS["post_monsoon"]


def predict_risk(
    weather_data: dict,
    season_month: Optional[int] = None,
    historical_avg_rain: Optional[float] = None,
) -> dict:
    """
    AI-driven risk assessment using weighted scoring.

    Args:
        weather_data: Current weather dict with rain_mm, temperature, humidity, aqi (optional).
        season_month: Month (1–12) for seasonal adjustment. Defaults to no adjustment.
        historical_avg_rain: Historical average rainfall for the location (optional).

    Returns:
        {
            "risk_score": 0.73,
            "premium_recommendation": 52,
            "risk_level": "high",
            "components": {
                "rainfall_risk": 0.65,
                "temperature_risk": 0.40,
                "pollution_risk": 0.15,
                "seasonal_factor": 1.4
            }
        }
    """
    rain_mm = weather_data.get("rain_mm", 0.0)
    temperature = weather_data.get("temperature", 30.0)
    humidity = weather_data.get("humidity", 50)
    aqi = weather_data.get("aqi", 50.0)

    # Calculate individual risk components
    rainfall_risk = calculate_rainfall_risk(rain_mm, humidity)
    temperature_risk = calculate_temperature_risk(temperature)
    pollution_risk = calculate_pollution_risk(aqi)

    # Weighted combination
    raw_score = (
        rainfall_risk * WEIGHT_RAINFALL
        + temperature_risk * WEIGHT_TEMPERATURE
        + pollution_risk * WEIGHT_POLLUTION
    )

    # Historical adjustment: if current rain is above historical average, increase risk
    if historical_avg_rain and historical_avg_rain > 0:
        deviation = rain_mm / historical_avg_rain
        if deviation > 1.5:
            raw_score = min(1.0, raw_score * 1.2)

    # Seasonal adjustment
    seasonal_factor = 1.0
    if season_month is not None:
        seasonal_factor = get_season_factor(season_month)
        raw_score = min(1.0, raw_score * seasonal_factor)

    risk_score = round(raw_score, 2)
    risk_level = classify_risk_level(risk_score)

    # Premium recommendation: linear interpolation within range
    premium = round(
        BASE_PREMIUM_MIN + (risk_score * (BASE_PREMIUM_MAX - BASE_PREMIUM_MIN)), 0
    )

    return {
        "risk_score": risk_score,
        "premium_recommendation": premium,
        "risk_level": risk_level,
        "components": {
            "rainfall_risk": round(rainfall_risk, 3),
            "temperature_risk": round(temperature_risk, 3),
            "pollution_risk": round(pollution_risk, 3),
            "seasonal_factor": seasonal_factor,
        },
    }

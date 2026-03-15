"""
ClimaShield – Weather Prediction Engine
Short-term disruption prediction using trend analysis.

Analyzes recent weather data points to predict likelihood
of disruptive events in the near future.
"""

from typing import Optional


# ── Disruption Thresholds ───────────────────────────────────────────

DISRUPTION_THRESHOLDS = {
    "rainfall": 40.0,     # mm
    "temperature": 45.0,  # °C
    "aqi": 300.0,         # AQI index
}


def analyze_trend(data_points: list[float]) -> dict:
    """
    Analyze a series of data points to detect trends.

    Args:
        data_points: List of sequential values (e.g., hourly rainfall readings).

    Returns:
        {
            "direction": "increasing" | "decreasing" | "stable",
            "rate_of_change": float,
            "volatility": float
        }
    """
    if len(data_points) < 2:
        return {"direction": "stable", "rate_of_change": 0.0, "volatility": 0.0}

    # Calculate changes between consecutive points
    changes = [data_points[i] - data_points[i - 1] for i in range(1, len(data_points))]
    avg_change = sum(changes) / len(changes)

    # Volatility: standard deviation of changes
    variance = sum((c - avg_change) ** 2 for c in changes) / len(changes)
    volatility = variance ** 0.5

    # Determine direction
    if avg_change > 0.5:
        direction = "increasing"
    elif avg_change < -0.5:
        direction = "decreasing"
    else:
        direction = "stable"

    return {
        "direction": direction,
        "rate_of_change": round(avg_change, 3),
        "volatility": round(volatility, 3),
    }


def predict_disruption(
    current_weather: dict,
    recent_history: Optional[list[dict]] = None,
) -> dict:
    """
    Predict likelihood of a disruptive weather event.

    Args:
        current_weather: Current weather data dict.
        recent_history: Optional list of recent weather readings for trend analysis.

    Returns:
        {
            "disruption_probability": 0.72,
            "predicted_event": "heavy_rainfall",
            "time_horizon": "6-12 hours",
            "confidence": 0.65,
            "trends": { ... }
        }
    """
    rain_mm = current_weather.get("rain_mm", 0.0)
    temperature = current_weather.get("temperature", 30.0)
    humidity = current_weather.get("humidity", 50)
    aqi = current_weather.get("aqi", 50.0)

    # Base disruption probabilities from current conditions
    rain_prob = _rain_disruption_probability(rain_mm, humidity)
    heat_prob = _heat_disruption_probability(temperature)
    pollution_prob = _pollution_disruption_probability(aqi)

    # Determine most likely disruption
    probabilities = {
        "heavy_rainfall": rain_prob,
        "extreme_heat": heat_prob,
        "severe_pollution": pollution_prob,
    }

    predicted_event = max(probabilities, key=probabilities.get)
    disruption_probability = probabilities[predicted_event]

    # Trend analysis if history is available
    trends = {}
    if recent_history and len(recent_history) >= 2:
        rain_trend = analyze_trend([h.get("rain_mm", 0) for h in recent_history])
        temp_trend = analyze_trend([h.get("temperature", 30) for h in recent_history])
        trends = {"rainfall_trend": rain_trend, "temperature_trend": temp_trend}

        # Boost probability if trend is increasing
        if rain_trend["direction"] == "increasing" and predicted_event == "heavy_rainfall":
            disruption_probability = min(1.0, disruption_probability * 1.3)
        if temp_trend["direction"] == "increasing" and predicted_event == "extreme_heat":
            disruption_probability = min(1.0, disruption_probability * 1.2)

    # Confidence based on data availability
    confidence = 0.5
    if recent_history:
        confidence = min(0.95, 0.5 + len(recent_history) * 0.05)

    # Time horizon estimate
    if disruption_probability > 0.7:
        time_horizon = "0-6 hours"
    elif disruption_probability > 0.4:
        time_horizon = "6-12 hours"
    else:
        time_horizon = "12-24 hours"

    return {
        "disruption_probability": round(disruption_probability, 2),
        "predicted_event": predicted_event,
        "time_horizon": time_horizon,
        "confidence": round(confidence, 2),
        "trends": trends,
        "all_probabilities": {k: round(v, 3) for k, v in probabilities.items()},
    }


def _rain_disruption_probability(rain_mm: float, humidity: float) -> float:
    """Estimate probability of heavy rainfall disruption."""
    if rain_mm >= 40:
        return min(1.0, 0.8 + (rain_mm - 40) / 100)
    rain_factor = rain_mm / 40
    humidity_boost = max(0, (humidity - 70) / 100)
    return min(1.0, rain_factor * 0.7 + humidity_boost * 0.3)


def _heat_disruption_probability(temperature: float) -> float:
    """Estimate probability of extreme heat disruption."""
    if temperature >= 45:
        return min(1.0, 0.85 + (temperature - 45) / 20)
    if temperature >= 38:
        return 0.4 + (temperature - 38) / 14
    return max(0.0, (temperature - 30) / 20)


def _pollution_disruption_probability(aqi: float) -> float:
    """Estimate probability of severe pollution disruption."""
    if aqi >= 300:
        return min(1.0, 0.8 + (aqi - 300) / 500)
    if aqi >= 200:
        return 0.4 + (aqi - 200) / 250
    return max(0.0, aqi / 500)

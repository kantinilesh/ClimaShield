"""
ClimaShield – Anomaly Detection
Detects anomalous weather patterns and potential fraud signals.

Methods:
  - Z-score detection for sudden spikes
  - IQR (Interquartile Range) for outlier detection
  - Pattern consistency checks
"""

import math
from typing import Optional


def detect_anomalies(
    current_reading: dict,
    historical_readings: Optional[list[dict]] = None,
) -> dict:
    """
    Detect anomalous weather patterns in current data.

    Args:
        current_reading: Current weather data dict.
        historical_readings: List of past weather readings for baseline.

    Returns:
        {
            "is_anomalous": True/False,
            "anomaly_score": 0.85,
            "anomalies": [
                {"field": "rain_mm", "type": "spike", "severity": "high", "z_score": 2.8}
            ],
            "fraud_flags": []
        }
    """
    anomalies = []
    fraud_flags = []

    if historical_readings and len(historical_readings) >= 3:
        # Z-score anomaly detection on each metric
        for field in ["rain_mm", "temperature", "humidity"]:
            current_val = current_reading.get(field, 0)
            historical_vals = [h.get(field, 0) for h in historical_readings]

            z_result = _z_score_check(current_val, historical_vals)
            if z_result["is_anomaly"]:
                anomalies.append({
                    "field": field,
                    "type": "spike" if z_result["z_score"] > 0 else "drop",
                    "severity": z_result["severity"],
                    "z_score": z_result["z_score"],
                    "current_value": current_val,
                    "expected_range": z_result["expected_range"],
                })

        # IQR outlier detection
        for field in ["rain_mm", "temperature"]:
            current_val = current_reading.get(field, 0)
            historical_vals = [h.get(field, 0) for h in historical_readings]

            iqr_result = _iqr_check(current_val, historical_vals)
            if iqr_result["is_outlier"] and not any(
                a["field"] == field for a in anomalies
            ):
                anomalies.append({
                    "field": field,
                    "type": "outlier",
                    "severity": "moderate",
                    "current_value": current_val,
                    "iqr_bounds": iqr_result["bounds"],
                })

        # Fraud detection: implausible values
        fraud_flags = _check_fraud_signals(current_reading)

    else:
        # Without history, only check for implausible values
        fraud_flags = _check_fraud_signals(current_reading)

    # Calculate overall anomaly score
    anomaly_score = _calculate_anomaly_score(anomalies, fraud_flags)

    return {
        "is_anomalous": len(anomalies) > 0 or len(fraud_flags) > 0,
        "anomaly_score": round(anomaly_score, 2),
        "anomalies": anomalies,
        "fraud_flags": fraud_flags,
    }


def _z_score_check(value: float, historical: list[float]) -> dict:
    """Check if a value is anomalous using z-score."""
    if not historical:
        return {"is_anomaly": False, "z_score": 0.0, "severity": "none", "expected_range": (0, 0)}

    mean = sum(historical) / len(historical)
    variance = sum((x - mean) ** 2 for x in historical) / len(historical)
    std_dev = max(variance ** 0.5, 0.01)  # Avoid division by zero

    z_score = (value - mean) / std_dev

    severity = "none"
    is_anomaly = False
    if abs(z_score) > 3:
        severity = "critical"
        is_anomaly = True
    elif abs(z_score) > 2:
        severity = "high"
        is_anomaly = True
    elif abs(z_score) > 1.5:
        severity = "moderate"
        is_anomaly = True

    return {
        "is_anomaly": is_anomaly,
        "z_score": round(z_score, 2),
        "severity": severity,
        "expected_range": (round(mean - 2 * std_dev, 2), round(mean + 2 * std_dev, 2)),
    }


def _iqr_check(value: float, historical: list[float]) -> dict:
    """Check if a value is an outlier using IQR method."""
    if len(historical) < 4:
        return {"is_outlier": False, "bounds": (0, 0)}

    sorted_data = sorted(historical)
    n = len(sorted_data)
    q1 = sorted_data[n // 4]
    q3 = sorted_data[3 * n // 4]
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return {
        "is_outlier": value < lower_bound or value > upper_bound,
        "bounds": (round(lower_bound, 2), round(upper_bound, 2)),
    }


def _check_fraud_signals(reading: dict) -> list[dict]:
    """Check for implausible values that may indicate data tampering."""
    flags = []

    rain = reading.get("rain_mm", 0)
    temp = reading.get("temperature", 25)
    humidity = reading.get("humidity", 50)

    # Implausible rainfall
    if rain > 200:
        flags.append({
            "type": "implausible_rainfall",
            "value": rain,
            "message": f"Rainfall {rain}mm is unusually extreme – verify source",
        })

    # Implausible temperature
    if temp > 55 or temp < -20:
        flags.append({
            "type": "implausible_temperature",
            "value": temp,
            "message": f"Temperature {temp}°C is outside plausible range",
        })

    # Inconsistent humidity + rain combination
    if rain > 30 and humidity < 30:
        flags.append({
            "type": "inconsistent_data",
            "value": {"rain": rain, "humidity": humidity},
            "message": "High rainfall with very low humidity is suspicious",
        })

    return flags


def _calculate_anomaly_score(anomalies: list, fraud_flags: list) -> float:
    """Calculate an overall anomaly score from detected anomalies."""
    score = 0.0

    severity_weights = {"critical": 0.4, "high": 0.25, "moderate": 0.15}
    for anomaly in anomalies:
        score += severity_weights.get(anomaly.get("severity", ""), 0.1)

    score += len(fraud_flags) * 0.3

    return min(1.0, score)

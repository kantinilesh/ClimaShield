"""
ClimaShield – Oracle Validator
Validates environmental data integrity before claim processing.

Checks:
  - Timestamp validity (data freshness)
  - Source reliability
  - Location consistency
  - Value plausibility
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("climashield.oracle_validator")


# ── Validation Configuration ────────────────────────────────────────

MAX_DATA_AGE_MINUTES = 30  # Data older than this is considered stale
PLAUSIBLE_RANGES = {
    "rain_mm": (0.0, 300.0),
    "temperature": (-30.0, 55.0),
    "humidity": (0, 100),
    "aqi": (0.0, 500.0),
}

TRUSTED_SOURCES = ["openweathermap", "mock"]  # Trusted data sources


def validate_oracle_data(
    weather_data: dict,
    expected_location: str,
    data_timestamp: Optional[str] = None,
) -> dict:
    """
    Validate environmental data before claim processing.

    Checks:
      1. Timestamp freshness
      2. Source reliability
      3. Location match
      4. Value plausibility

    Args:
        weather_data: Weather data dict to validate.
        expected_location: Expected city/location name.
        data_timestamp: ISO timestamp of when data was fetched (optional).

    Returns:
        {
            "valid": True/False,
            "confidence": 0.91,
            "checks": {
                "timestamp": {"passed": True, "detail": "..."},
                "source": {"passed": True, "detail": "..."},
                "location": {"passed": True, "detail": "..."},
                "plausibility": {"passed": True, "detail": "..."}
            }
        }
    """
    checks = {}
    total_weight = 0.0
    weighted_score = 0.0

    # ── 1. Timestamp freshness (weight: 0.25) ──
    ts_check = _check_timestamp(data_timestamp)
    checks["timestamp"] = ts_check
    total_weight += 0.25
    weighted_score += 0.25 * (1.0 if ts_check["passed"] else 0.3)

    # ── 2. Source reliability (weight: 0.25) ──
    source_check = _check_source(weather_data)
    checks["source"] = source_check
    total_weight += 0.25
    weighted_score += 0.25 * (1.0 if source_check["passed"] else 0.2)

    # ── 3. Location consistency (weight: 0.25) ──
    location_check = _check_location(weather_data, expected_location)
    checks["location"] = location_check
    total_weight += 0.25
    weighted_score += 0.25 * (1.0 if location_check["passed"] else 0.0)

    # ── 4. Value plausibility (weight: 0.25) ──
    plausibility_check = _check_plausibility(weather_data)
    checks["plausibility"] = plausibility_check
    total_weight += 0.25
    weighted_score += 0.25 * (1.0 if plausibility_check["passed"] else 0.1)

    confidence = round(weighted_score / total_weight, 2) if total_weight > 0 else 0.0
    all_passed = all(c["passed"] for c in checks.values())

    result = {
        "valid": all_passed,
        "confidence": confidence,
        "checks": checks,
    }

    logger.info(
        f"[VALIDATOR] {expected_location}: valid={all_passed}, confidence={confidence}"
    )

    return result


def _check_timestamp(data_timestamp: Optional[str]) -> dict:
    """Check that data is recent enough to be trustworthy."""
    if data_timestamp is None:
        # No timestamp provided — assume fresh (just fetched)
        return {"passed": True, "detail": "No timestamp — assumed fresh (just fetched)"}

    try:
        ts = datetime.fromisoformat(data_timestamp.replace("Z", "+00:00"))
        now = datetime.utcnow().replace(tzinfo=ts.tzinfo)
        age = now - ts
        age_minutes = age.total_seconds() / 60

        if age_minutes <= MAX_DATA_AGE_MINUTES:
            return {"passed": True, "detail": f"Data is {age_minutes:.0f} min old (fresh)"}
        else:
            return {"passed": False, "detail": f"Data is {age_minutes:.0f} min old (stale, max {MAX_DATA_AGE_MINUTES} min)"}
    except Exception as e:
        return {"passed": False, "detail": f"Invalid timestamp format: {e}"}


def _check_source(weather_data: dict) -> dict:
    """Check that data comes from a trusted source."""
    source = weather_data.get("source", "unknown")

    # Accept any source that starts with a trusted prefix
    for trusted in TRUSTED_SOURCES:
        if source.startswith(trusted):
            return {"passed": True, "detail": f"Source '{source}' is trusted"}

    return {"passed": False, "detail": f"Source '{source}' is not in trusted sources"}


def _check_location(weather_data: dict, expected_location: str) -> dict:
    """Check that data location matches expected location."""
    data_city = weather_data.get("city", "").lower().strip()
    expected = expected_location.lower().strip()

    if data_city == expected:
        return {"passed": True, "detail": f"Location matches: {expected_location}"}

    # Fuzzy match: check if one contains the other
    if data_city in expected or expected in data_city:
        return {"passed": True, "detail": f"Location fuzzy match: '{data_city}' ≈ '{expected}'"}

    return {
        "passed": False,
        "detail": f"Location mismatch: expected '{expected_location}', got '{weather_data.get('city', 'unknown')}'",
    }


def _check_plausibility(weather_data: dict) -> dict:
    """Check that all values are within plausible physical ranges."""
    issues = []

    for field, (low, high) in PLAUSIBLE_RANGES.items():
        value = weather_data.get(field)
        if value is not None and (value < low or value > high):
            issues.append(f"{field}={value} outside range [{low}, {high}]")

    if issues:
        return {"passed": False, "detail": f"Implausible values: {'; '.join(issues)}"}

    return {"passed": True, "detail": "All values within plausible ranges"}

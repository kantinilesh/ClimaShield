"""
ClimaShield – Rule Engine
Parametric trigger rules for automated insurance claim verification.

Supports:
  - rainfall_threshold
  - temperature_threshold
  - aqi_threshold
"""

from typing import Optional


def rainfall_trigger(data: dict, threshold: float) -> tuple[bool, Optional[str]]:
    """
    Check if rainfall exceeds the threshold.

    Args:
        data: Weather data dict with 'rain_mm' key.
        threshold: Rainfall threshold in mm.

    Returns:
        (triggered: bool, reason: Optional[str])
    """
    rain_mm = data.get("rain_mm", 0.0)
    if rain_mm > threshold:
        return True, f"rainfall_threshold_exceeded (actual: {rain_mm}mm > threshold: {threshold}mm)"
    return False, None


def temperature_trigger(data: dict, threshold: float) -> tuple[bool, Optional[str]]:
    """
    Check if temperature exceeds the threshold (extreme heat).

    Args:
        data: Weather data dict with 'temperature' key.
        threshold: Temperature threshold in °C.

    Returns:
        (triggered: bool, reason: Optional[str])
    """
    temperature = data.get("temperature", 0.0)
    if temperature > threshold:
        return True, f"temperature_threshold_exceeded (actual: {temperature}°C > threshold: {threshold}°C)"
    return False, None


def aqi_trigger(data: dict, threshold: float) -> tuple[bool, Optional[str]]:
    """
    Check if AQI (Air Quality Index) exceeds the threshold.

    Args:
        data: Weather/environment data dict with 'aqi' key.
        threshold: AQI threshold.

    Returns:
        (triggered: bool, reason: Optional[str])
    """
    aqi = data.get("aqi", 0.0)
    if aqi > threshold:
        return True, f"aqi_threshold_exceeded (actual: {aqi} > threshold: {threshold})"
    return False, None


def flood_alert_trigger(data: dict, threshold: float) -> tuple[bool, Optional[str]]:
    """
    Check if a flood alert flag is active.

    Args:
        data: Weather/environment data dict with 'flood_alert' key (0 or 1).
        threshold: Threshold (typically 1.0 – any alert triggers).

    Returns:
        (triggered: bool, reason: Optional[str])
    """
    flood_flag = data.get("flood_alert", 0.0)
    if flood_flag >= threshold:
        return True, f"flood_alert_active (alert level: {flood_flag})"
    return False, None


# Registry mapping coverage types to their trigger functions
TRIGGER_REGISTRY = {
    "rainfall": rainfall_trigger,
    "temperature": temperature_trigger,
    "aqi": aqi_trigger,
    "flood_alert": flood_alert_trigger,
}


def evaluate_trigger(
    coverage_type: str, weather_data: dict, threshold: float
) -> tuple[bool, Optional[str]]:
    """
    Evaluate the appropriate trigger for a given coverage type.

    Args:
        coverage_type: One of 'rainfall', 'temperature', 'aqi'.
        weather_data: Current environmental data.
        threshold: The threshold value from the policy.

    Returns:
        (triggered: bool, reason: Optional[str])

    Raises:
        ValueError: If coverage_type is not supported.
    """
    trigger_fn = TRIGGER_REGISTRY.get(coverage_type)
    if trigger_fn is None:
        raise ValueError(
            f"Unsupported coverage type: '{coverage_type}'. "
            f"Supported types: {list(TRIGGER_REGISTRY.keys())}"
        )
    return trigger_fn(weather_data, threshold)

"""
ClimaShield – Dataset Manager
High-level interface for managing LazAI oracle datasets.

Provides convenient methods for storing, retrieving,
and verifying oracle event data.
"""

import logging
from typing import Optional

from lazai.lazai_client import (
    store_event,
    get_event,
    get_events_by_city,
    get_all_events,
    verify_proof,
)
from oracle.oracle_validator import validate_oracle_data

logger = logging.getLogger("climashield.dataset_manager")


async def store_oracle_event(
    event_type: str,
    value: float,
    threshold: float,
    location: str,
    weather_data: dict,
) -> dict:
    """
    Validate and store an oracle event to LazAI.

    Flow:
      1. Validate the weather data through oracle validator
      2. Store the event with validation proof
      3. Return the stored record

    Args:
        event_type: Trigger type (rainfall, temperature, aqi).
        value: Measured value.
        threshold: Policy threshold that was exceeded.
        location: City name.
        weather_data: Full weather data snapshot.

    Returns:
        Stored dataset record including validation and dataset_id.
    """
    # Validate data before storing
    validation = validate_oracle_data(weather_data, location)

    # Store with validation proof
    record = store_event(
        event_type=event_type,
        value=value,
        threshold=threshold,
        location=location,
        weather_data=weather_data,
        validation=validation,
    )

    logger.info(
        f"[DATASET] Stored oracle event: {record['dataset_id']} "
        f"(valid={validation['valid']}, confidence={validation['confidence']})"
    )

    return record


def get_oracle_history(city: str, limit: int = 20) -> list[dict]:
    """
    Retrieve historical oracle events for a city.

    Args:
        city: City name.
        limit: Maximum number of records to return.

    Returns:
        List of event records, most recent first.
    """
    return get_events_by_city(city, limit=limit)


def get_latest_events(limit: int = 10) -> list[dict]:
    """Get the most recent oracle events across all cities."""
    return get_all_events(limit=limit)


def verify_claim_proof(dataset_id: str) -> dict:
    """
    Verify that a claim's proof dataset exists and is valid.

    This is used during the claim payout process to ensure
    the triggering event has been properly recorded and verified.

    Args:
        dataset_id: The LazAI dataset ID from the claim.

    Returns:
        {
            "verified": True/False,
            "dataset_id": "...",
            "event_type": "rainfall",
            "location": "Mumbai",
            "timestamp": "...",
            "storage_layer": "lazai_local"
        }
    """
    return verify_proof(dataset_id)

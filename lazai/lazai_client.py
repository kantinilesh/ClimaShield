"""
ClimaShield – LazAI Client
Verifiable oracle data storage layer.

Stores disruption events as immutable datasets that serve as
proof for automated insurance payouts.

Phase 2: Uses local JSON storage.
Phase 3: Will connect to LazAI on-chain storage.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("climashield.lazai")

# Local storage path (swappable for on-chain in Phase 3)
LAZAI_STORE_PATH = Path(__file__).parent.parent / "data" / "lazai_datasets.json"


def _load_store() -> list[dict]:
    """Load the LazAI dataset store."""
    if not LAZAI_STORE_PATH.exists():
        return []
    with open(LAZAI_STORE_PATH, "r") as f:
        return json.load(f)


def _save_store(datasets: list[dict]) -> None:
    """Persist the LazAI dataset store."""
    LAZAI_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LAZAI_STORE_PATH, "w") as f:
        json.dump(datasets, f, indent=2, default=str)


def generate_dataset_id(event_type: str, location: str) -> str:
    """Generate a unique dataset ID for an oracle event."""
    date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    city_slug = location.lower().replace(" ", "_")
    return f"oracle_{date_str}_{city_slug}_{event_type}"


def store_event(
    event_type: str,
    value: float,
    threshold: float,
    location: str,
    weather_data: Optional[dict] = None,
    validation: Optional[dict] = None,
) -> dict:
    """
    Store a verified oracle event as an immutable dataset.

    Args:
        event_type: Type of event (e.g., "rainfall", "temperature").
        value: Measured value that triggered the event.
        threshold: Threshold that was exceeded.
        location: City/region name.
        weather_data: Full weather snapshot at the time.
        validation: Oracle validation result.

    Returns:
        The stored dataset record with its unique ID.
    """
    dataset_id = generate_dataset_id(event_type, location)

    record = {
        "dataset_id": dataset_id,
        "event_type": event_type,
        "value": value,
        "threshold": threshold,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": location,
        "weather_snapshot": weather_data,
        "validation": validation,
        "status": "verified",
        "storage_layer": "lazai_local",  # Will become "lazai_chain" in Phase 3
    }

    datasets = _load_store()
    datasets.append(record)
    _save_store(datasets)

    logger.info(f"[LAZAI] Stored event: {dataset_id}")
    return record


def get_event(dataset_id: str) -> Optional[dict]:
    """Retrieve a specific dataset by ID."""
    datasets = _load_store()
    for ds in datasets:
        if ds["dataset_id"] == dataset_id:
            return ds
    return None


def get_events_by_city(city: str, limit: int = 20) -> list[dict]:
    """Retrieve all oracle events for a specific city."""
    datasets = _load_store()
    city_events = [
        ds for ds in datasets
        if ds.get("location", "").lower() == city.lower()
    ]
    # Return most recent first
    city_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return city_events[:limit]


def get_all_events(limit: int = 50) -> list[dict]:
    """Retrieve all oracle events, most recent first."""
    datasets = _load_store()
    datasets.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return datasets[:limit]


def verify_proof(dataset_id: str) -> dict:
    """
    Verify that a proof dataset exists and is valid.
    Used during claim verification to confirm data integrity.
    """
    record = get_event(dataset_id)
    if record is None:
        return {"verified": False, "reason": "Dataset not found"}

    return {
        "verified": True,
        "dataset_id": dataset_id,
        "event_type": record["event_type"],
        "location": record["location"],
        "timestamp": record["timestamp"],
        "storage_layer": record.get("storage_layer", "unknown"),
    }

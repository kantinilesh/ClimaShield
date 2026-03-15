"""
ClimaShield – Centralized Logging Service
Structured logging for all system events.

Logs to:
  - Console (colored)
  - logs/system.log (JSON-structured)
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "system.log"
EVENT_LOG = LOGS_DIR / "events.json"


def setup_logging():
    """
    Configure centralized logging for the entire application.
    Call this once at app startup.
    """
    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    ))

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    ))

    # Add handlers (avoid duplicates)
    if not root.handlers:
        root.addHandler(console)
        root.addHandler(file_handler)


def log_event(
    category: str,
    message: str,
    data: Optional[dict] = None,
    level: str = "info",
) -> dict:
    """
    Log a structured event to the events log.

    Args:
        category: Event category (e.g. 'policy_create', 'oracle_trigger')
        message: Human-readable message.
        data: Optional structured data.
        level: Log level (info, warning, error).

    Returns:
        The event record that was logged.
    """
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "category": category,
        "message": message,
        "level": level,
    }
    if data:
        event["data"] = data

    # Append to events log
    events = _load_events()
    events.append(event)

    # Keep last 500 events
    if len(events) > 500:
        events = events[-500:]

    _save_events(events)

    # Also log to Python logger
    logger = logging.getLogger(f"climashield.{category}")
    log_fn = getattr(logger, level, logger.info)
    log_fn(message)

    return event


def get_recent_events(limit: int = 50, category: Optional[str] = None) -> list:
    """
    Get recent events from the log.

    Args:
        limit: Max events to return.
        category: Optional filter by category.
    """
    events = _load_events()
    if category:
        events = [e for e in events if e.get("category") == category]
    return events[-limit:]


def get_event_summary() -> dict:
    """Get summary of logged events by category."""
    events = _load_events()
    categories = {}
    for e in events:
        cat = e.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "total_events": len(events),
        "categories": categories,
    }


def _load_events() -> list:
    if not EVENT_LOG.exists():
        return []
    try:
        with open(EVENT_LOG, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def _save_events(events: list):
    with open(EVENT_LOG, "w") as f:
        json.dump(events, f, indent=2, default=str)


# Auto-setup on import
setup_logging()

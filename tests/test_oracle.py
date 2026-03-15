"""
ClimaShield – Test Suite: Oracle & Risk
Tests for oracle monitoring, risk assessment, and trigger evaluation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.rule_engine import evaluate_trigger
from oracle.oracle_validator import validate_oracle_data


def test_rainfall_trigger_fires():
    """Test rainfall trigger fires above threshold."""
    triggered, reason = evaluate_trigger("rainfall", {"rain_mm": 45}, 40.0)
    assert triggered is True
    assert "45" in reason


def test_rainfall_trigger_no_fire():
    """Test rainfall trigger doesn't fire below threshold."""
    triggered, reason = evaluate_trigger("rainfall", {"rain_mm": 30}, 40.0)
    assert triggered is False


def test_temperature_trigger():
    """Test temperature trigger fires above threshold."""
    triggered, reason = evaluate_trigger("temperature", {"temperature": 46}, 42.0)
    assert triggered is True


def test_aqi_trigger():
    """Test AQI trigger fires above threshold."""
    triggered, reason = evaluate_trigger("aqi", {"aqi": 350}, 300.0)
    assert triggered is True


def test_flood_alert_trigger():
    """Test flood alert trigger."""
    triggered, reason = evaluate_trigger("flood_alert", {"flood_alert": 1.0}, 1.0)
    assert triggered is True


def test_oracle_validator_valid():
    """Test oracle validator passes for valid data."""
    data = {
        "city": "Mumbai",
        "rain_mm": 42,
        "temperature": 28,
        "humidity": 88,
        "source": "openweathermap",
    }
    result = validate_oracle_data(data, expected_location="Mumbai")
    assert result["valid"] is True
    assert result["confidence"] > 0.5


def test_oracle_validator_wrong_location():
    """Test oracle validator detects location mismatch."""
    data = {
        "city": "Delhi",
        "rain_mm": 42,
        "temperature": 28,
        "source": "openweathermap",
    }
    result = validate_oracle_data(data, expected_location="Mumbai")
    assert result["confidence"] < 1.0


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_risk_endpoint():
    """Test AI risk assessment endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/risk/Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert "risk_assessment" in data
    assert "disruption_prediction" in data
    assert "anomaly_report" in data


@pytest.mark.anyio
async def test_oracle_latest():
    """Test oracle latest events endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/oracle/latest")
    assert response.status_code == 200
    assert "events" in response.json()

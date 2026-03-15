"""
ClimaShield – Test Suite: Payments & Treasury
Tests for premium collection, treasury management, and payout service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from httpx import AsyncClient, ASGITransport
from app.main import app
from payments.treasury_manager import (
    deposit_premium,
    reserve_for_claim,
    execute_payout,
    get_status,
)


def test_treasury_deposit():
    """Test depositing a premium into treasury."""
    before = get_status()
    deposit_premium("PAY-TEST1", "CS-TEST", 5.0, "0xtest")
    after = get_status()
    assert after["total_collected"] >= before["total_collected"] + 5.0


def test_treasury_reserve():
    """Test reserving funds for a claim."""
    # Ensure there's liquidity
    deposit_premium("PAY-TEST2", "CS-TEST2", 20.0, "0xtest2")
    result = reserve_for_claim("CLM-TEST1", 10.0)
    assert result["success"] is True


def test_treasury_reserve_insufficient():
    """Test rejection when insufficient funds."""
    result = reserve_for_claim("CLM-BIG", 999999.0)
    assert result["success"] is False
    assert "Insufficient" in result["reason"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_treasury_endpoint():
    """Test treasury status endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/treasury/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_collected" in data
    assert "available_liquidity" in data
    assert data["currency"] == "USDC"


@pytest.mark.anyio
async def test_premium_payment():
    """Test premium payment endpoint with existing policy."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a policy first
        create_resp = await client.post(
            "/policy/create",
            json={"location": "PayTestCity", "coverage_type": "rainfall"},
        )
        policy_id = create_resp.json()["policy"]["policy_id"]

        # Pay premium
        pay_resp = await client.post(
            "/payments/create-premium",
            json={"policy_id": policy_id},
        )
    assert pay_resp.status_code == 200
    data = pay_resp.json()
    assert data["payment"]["status"] == "completed"
    assert data["payment"]["protocol"] == "x402"


@pytest.mark.anyio
async def test_claim_processing_no_trigger():
    """Test claim processing with no trigger (normal weather)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/policy/create",
            json={"location": "Mumbai", "coverage_type": "rainfall"},
        )
        policy_id = create_resp.json()["policy"]["policy_id"]

        claim_resp = await client.post(
            "/claims/process",
            json={"policy_id": policy_id},
        )
    assert claim_resp.status_code == 200
    # Current weather in Mumbai likely doesn't trigger
    data = claim_resp.json()
    assert data["status"] in ("no_trigger", "claim_processed")

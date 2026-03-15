"""
ClimaShield – Test Suite: Policy Management
Tests for policy creation, retrieval, and cancellation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_check():
    """Test health endpoint returns phase 4."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ClimaShield"


@pytest.mark.anyio
async def test_create_policy():
    """Test creating a new policy."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/policy/create",
            json={"location": "TestCity", "coverage_type": "rainfall"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Policy created"
    assert data["policy"]["location"] == "TestCity"
    assert data["policy"]["coverage_type"] == "rainfall"
    assert data["policy"]["status"] == "active"


@pytest.mark.anyio
async def test_get_policy():
    """Test retrieving a policy."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create first
        create_resp = await client.post(
            "/policy/create",
            json={"location": "TestCity2", "coverage_type": "temperature"},
        )
        policy_id = create_resp.json()["policy"]["policy_id"]

        # Retrieve
        response = await client.get(f"/policy/{policy_id}")
    assert response.status_code == 200
    assert response.json()["policy"]["policy_id"] == policy_id


@pytest.mark.anyio
async def test_policy_not_found():
    """Test 404 for missing policy."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/policy/FAKE999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_invalid_coverage_type():
    """Test rejection of invalid coverage type."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/policy/create",
            json={"location": "TestCity", "coverage_type": "earthquake"},
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_list_policies():
    """Test listing all policies."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/policies")
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data
    assert "total" in data


@pytest.mark.anyio
async def test_agent_identity():
    """Test agent identity endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/agent/identity")
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data

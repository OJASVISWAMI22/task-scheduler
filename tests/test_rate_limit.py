import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

pytestmark = pytest.mark.asyncio

async def test_rate_limit_not_exceeded(app_client, mock_redis):
    """9 requests — sab pass hone chahiye"""
    mock_redis.get = AsyncMock(return_value=b"5")
    async with app_client as client:
        response = await client.post(
            "/process",
            json={
                "user_id": "usr_123",
                "user_name": "utkarsh",
                "payload": "Hello",
                "operation": "Encrypt",
                "priority": 1
            },
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 200

async def test_rate_limit_exceeded(app_client, mock_redis):
    """10+ requests — 429 aana chahiye"""
    mock_redis.get = AsyncMock(return_value=b"10")
    mock_redis.ttl = AsyncMock(return_value=45)
    async with app_client as client:
        response = await client.post(
            "/process",
            json={
                "user_id": "usr_123",
                "user_name": "utkarsh",
                "payload": "Hello",
                "operation": "Encrypt",
                "priority": 1
            },
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 429
    data = response.json()
    assert "retry_after_seconds" in data
    assert data["retry_after_seconds"] == 45

async def test_missing_user_id_header(app_client):
    """x-user-id header missing — 400 aana chahiye"""
    async with app_client as client:
        response = await client.post(
            "/process",
            json={
                "user_id": "usr_123",
                "user_name": "utkarsh",
                "payload": "Hello",
                "operation": "Encrypt",
                "priority": 1
            }
        )
    assert response.status_code == 400
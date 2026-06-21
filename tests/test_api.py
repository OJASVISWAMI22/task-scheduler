import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

pytestmark = pytest.mark.asyncio

async def test_post_process_happy_path(app_client, mock_db, mock_redis):
    """POST /process valid request — 200 aana chahiye, request_id milna chahiye"""
    async with app_client as client:
        response = await client.post(
            "/process",
            json={
                "user_id": "usr_123",
                "user_name": "utkarsh",
                "payload": "Hello World",
                "operation": "Encrypt",
                "priority": 1
            },
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["status"] == "pending"

async def test_post_process_invalid_operation(app_client):
    """POST /process invalid operation — 422 aana chahiye"""
    async with app_client as client:
        response = await client.post(
            "/process",
            json={
                "user_id": "usr_123",
                "user_name": "utkarsh",
                "payload": "Hello World",
                "operation": "INVALID_OP",
                "priority": 1
            },
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 422

async def test_get_status_not_found(app_client, mock_db):
    """GET /status unknown id — 404 aana chahiye"""
    mock_db.fetchrow = AsyncMock(return_value=None)
    async with app_client as client:
        response = await client.get(
            f"/status/{uuid4()}",
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 404

async def test_get_status_found(app_client, mock_db):
    """GET /status valid id — 200 aana chahiye with status"""
    from datetime import datetime, timezone
    request_id = uuid4()
    mock_db.fetchrow = AsyncMock(return_value={
        "id": request_id,
        "status": "done",
        "created_at": datetime.now(timezone.utc),
        "output_data": "encrypted_string",
        "processing_time": 12,
        "processed_at": datetime.now(timezone.utc)
    })
    async with app_client as client:
        response = await client.get(
            f"/status/{request_id}",
            headers={"x-user-id": "usr_123"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["output_data"] == "encrypted_string"
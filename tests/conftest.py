import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.dependencies import get_db, get_redis

@pytest.fixture
def mock_db():
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.execute = AsyncMock(return_value=None)
    return conn

@pytest.fixture
def mock_redis():
    r = AsyncMock()
    r.get = AsyncMock(return_value=None)
    r.incr = AsyncMock(return_value=1)
    r.expire = AsyncMock(return_value=True)
    r.ttl = AsyncMock(return_value=45)
    r.lpush = AsyncMock(return_value=1)
    return r

@pytest.fixture
def app_client(mock_db, mock_redis):
    async def override_get_db():
        yield mock_db

    async def override_get_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    with patch("app.main.init_db_pool", new_callable=AsyncMock), \
         patch("app.main.init_redis_pool", new_callable=AsyncMock), \
         patch("app.main.close_db_pool", new_callable=AsyncMock), \
         patch("app.main.close_redis_pool", new_callable=AsyncMock), \
         patch("app.main.get_pool", return_value=AsyncMock()), \
         patch("app.main.get_redis_pool", return_value=mock_redis), \
         patch("app.database.get_redis_pool", return_value=mock_redis), \
         patch("app.middleware.get_redis_pool", return_value=mock_redis), \
         patch("app.worker.worker", new_callable=AsyncMock):
        yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
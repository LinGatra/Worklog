import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import db_connect
from app.main import app


@pytest.fixture
async def client(session):
    async def override_db_connect():
        yield session

    app.dependency_overrides[db_connect] = override_db_connect

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac

    app.dependency_overrides.clear()

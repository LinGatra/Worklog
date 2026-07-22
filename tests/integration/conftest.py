import pytest
from httpx import AsyncClient


@pytest.fixture(scope='function')
async def client(app_environment):
    async with AsyncClient(base_url=app_environment['app_url'], timeout=10) as client:
        yield client

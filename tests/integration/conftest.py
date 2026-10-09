from random import randint

import pytest
from httpx import AsyncClient


@pytest.fixture(scope='function')
async def api_client(app_environment):
    async with AsyncClient(base_url=app_environment['app_url'], timeout=10) as api_client:
        yield api_client


@pytest.fixture(scope='function')
async def create_client_fixture(api_client):

    create_request_body = {'client_name': f'{randint(1, 2**16)}'}
    response = await api_client.post('/client/', json=create_request_body)
    created_client_id = response.json()['id']
    return created_client_id


@pytest.fixture(scope='function')
async def create_offering_fixture(api_client):

    create_request_body = {'offering_name': f'{randint(1, 2**16)}', 'offering_price': 100}
    response = await api_client.post('/offering/', json=create_request_body)
    created_offering_id = response.json()['id']
    return created_offering_id


@pytest.fixture(scope='function')
async def create_alt_price_fixture(api_client, create_client_fixture, create_offering_fixture):

    client_id = create_client_fixture
    offering_id = create_offering_fixture
    create_request_body = {'client_id': client_id, 'offering_id': offering_id, 'alt_price': 1000}
    response = await api_client.post('/alt-price/', json=create_request_body)
    created_alt_price_id = response.json()['id']
    return created_alt_price_id

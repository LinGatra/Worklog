import pytest

pytestmark = pytest.mark.asyncio(loop_scope='session')


@pytest.mark.integration
async def test_client_happy_lifecycle(api_client):
    # check that there is no clients initially
    response = await api_client.get('/client/')
    assert response.status_code == 200
    assert response.json() == []

    # create valid client
    create_request_body = {'client_name': 'Valid Client'}
    response = await api_client.post('/client/', json=create_request_body)
    assert response.status_code == 200
    data = response.json()
    assert data != []
    assert type(data['id']) is int
    assert type(data['client_name']) is str

    created_client_id = data['id']
    created_client_name = data['client_name']

    # update created client
    update_request_body = {'client_name': 'Updated Client'}
    response = await api_client.patch(f'/client/{created_client_id}', json=update_request_body)
    assert response.status_code == 200
    data = response.json()
    assert data != []
    assert data['id'] == created_client_id
    assert data['client_name'] != created_client_name

    # delete client
    response = await api_client.delete(f'/client/{created_client_id}')
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.integration
async def test_offering_happy_lifecycle(api_client):
    # check that there is no offerings initially
    response = await api_client.get('/offering/')
    assert response.status_code == 200
    assert response.json() == []

    # create valid offering
    create_request_body = {'offering_name': 'Valid Offering', 'offering_price': 1000}
    response = await api_client.post('/offering/', json=create_request_body)
    assert response.status_code == 200
    data = response.json()
    assert data != []
    assert type(data['id']) is int
    assert type(data['offering_name']) is str
    assert type(data['offering_price']) is int
    assert data['offering_price'] == 1000

    created_offering_id = data['id']
    created_offering_name = data['offering_name']

    # update created offering
    update_request_body = {'offering_name': 'Updated Offering', 'offering_price': 2000}
    response = await api_client.patch(f'/offering/{created_offering_id}', json=update_request_body)
    assert response.status_code == 200
    data = response.json()
    assert data != []
    assert data['id'] == created_offering_id
    assert data['offering_name'] != created_offering_name
    assert data['offering_price'] == 2000

    # delete offering
    response = await api_client.delete(f'/offering/{created_offering_id}')
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.integration
async def test_alt_price_happy_lifecycle(
    api_client, create_client_fixture, create_offering_fixture
):
    client_id = create_client_fixture
    offering_id = create_offering_fixture

    # check that there is no alt prices initially
    response = await api_client.get('/alt-price/')
    assert response.status_code == 200
    assert response.json() == []

    # create alt price
    create_request_body = {'client_id': client_id, 'offering_id': offering_id, 'alt_price': 70}
    response = await api_client.post('/alt-price/', json=create_request_body)
    assert response.status_code == 200
    data = response.json()
    assert data != []
    created_alt_price_id = data['id']

    assert type(data['id']) is int
    assert data['client_id'] == client_id
    assert data['offering_id'] == offering_id
    assert data['alt_price'] == 70

    # update alt price
    update_request_body = {'alt_price': 73}
    response = await api_client.patch(
        f'/alt-price/{created_alt_price_id}', json=update_request_body
    )
    assert response.status_code == 200
    data = response.json()
    assert data != []
    assert data['id'] == created_alt_price_id
    assert data['client_id'] == client_id
    assert data['offering_id'] == offering_id
    assert data['alt_price'] == 73

    # delete alt price
    response = await api_client.delete(f'/alt-price/{created_alt_price_id}')
    assert response.status_code == 200
    assert response.json() is None

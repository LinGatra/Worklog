import pytest

pytestmark = pytest.mark.asyncio(loop_scope='session')


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames='client_name',
    argvalues=[
        '',  # name can not be empty
        'This string is definitely longer than one hundred characters, so it should not pass the validation filter',  # name must be shorter than 100 symbols
        '象形文字で書かれた抽象的な一行',  # only english and cyrillic letters
    ],
)
async def test_create_client_validation_edge_cases(api_client, client_name):
    create_request_body = {'client_name': client_name}
    result = await api_client.post('/client/', json=create_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_create_client_already_exists(api_client):
    create_request_body = {'client_name': 'Client'}
    successfull_request = await api_client.post('/client/', json=create_request_body)
    assert successfull_request.status_code == 200
    failed_result = await api_client.post('/client/', json=create_request_body)
    assert failed_result.status_code == 409


@pytest.mark.integration
@pytest.mark.parametrize(argnames='id', argvalues=(-1, 3.141592, 1_000_001, 'string', None, dict))
async def test_read_client_validation_edge_cases(api_client, id):
    result = await api_client.get(f'/client/{id}')
    assert result.status_code == 422


@pytest.mark.integration
async def test_read_client_not_found(api_client):
    result = await api_client.get('/client/100000')
    assert result.status_code == 404


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames='client_name',
    argvalues=[
        '',
        'This string is definitely longer than one hundred characters, so it should not pass the validation filter',
        '象形文字で書かれた抽象的な一行',
    ],
)
async def test_update_client_validation_edge_cases(api_client, create_client_fixture, client_name):
    create_request_body = {'client_name': client_name}
    id = create_client_fixture
    result = await api_client.patch(f'/client/{id}', json=create_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_update_client_not_found(api_client):
    update_request_budy = {'client_name': 'Valid Name'}
    result = await api_client.patch('/client/100000', json=update_request_budy)
    assert result.status_code == 404


# async def test_delete_client_edge_cases(api_client, create_client_fixture): ...
# IN ALL CASES THE `DELETE` REQUESTS RETURNS [200, Null].
# IS IT SUPPOSED TO BE LIKE THIS?


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames=('offering_name', 'offering_price'),
    argvalues=(
        ('Valid Name', None),  # price can not be Null
        ('', 100),  # name can not be empty
        (
            'This string is definitely longer than one hundred characters, so it should not pass the validation filter',
            1000,
        ),  # name must be shorter than 100 symbols
        ('象形文字で書かれた抽象的な一行', 100),  # only english and cyrillic letters
        ('Valid Name', -100),  # price must be greather or equal 0
        ('Valid Name', 1_000_001),  # price must be less than 1.000.000
        ('Valid Name', 3.141592),  # ?
        ('Valid Name', 'This is a string...'),  # price must be an integer
        # ('valid_name_1', 100),  # already exists
    ),
)
async def test_create_offering_validation_edge_cases(api_client, offering_name, offering_price):
    create_request_body = {'offering_name': offering_name, 'offering_price': offering_price}
    result = await api_client.post('/offering/', json=create_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_create_offering_already_exists(api_client):
    create_request_body = {'offering_name': 'Offering', 'offering_price': 1000}
    successfull_request = await api_client.post('/offering/', json=create_request_body)
    assert successfull_request.status_code == 200
    failed_result = await api_client.post('/offering/', json=create_request_body)
    assert failed_result.status_code == 409


@pytest.mark.integration
@pytest.mark.parametrize(argnames='id', argvalues=(-1, 3.141592, 1_000_001, 'string', None, dict))
async def test_read_offering_validation_edge_cases(api_client, id):
    result = await api_client.get(f'/offering/{id}')
    assert result.status_code == 422


@pytest.mark.integration
async def test_read_offering_not_found(api_client):
    result = await api_client.get('/offering/100000')
    assert result.status_code == 404


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames=('offering_name', 'offering_price'),
    argvalues=(
        ('Valid Name', None),  # price can not be Null
        ('', 100),  # name can not be empty
        (
            'This string is definitely longer than one hundred characters, so it should not pass the validation filter',
            1000,
        ),  # name must be shorter than 100 symbols
        ('象形文字で書かれた抽象的な一行', 100),  # only english and cyrillic letters
        ('Valid Name', -100),  # price must be greather or equal 0
        ('Valid Name', 1_000_001),  # price must be less than 1.000.000
        ('Valid Name', 3.141592),  # ?
        ('Valid Name', 'This is a string...'),  # price must be an integer
        # ('valid_name_1', 100),  # already exists
    ),
)
async def test_update_offering_validation_edge_cases(
    api_client, offering_name, offering_price, create_offering_fixture
):
    id = create_offering_fixture
    update_request_body = {'offering_name': offering_name, 'offering_price': offering_price}
    result = await api_client.patch(f'/offering/{id}', json=update_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_update_offering_not_found(api_client):
    update_request_budy = {'offering_name': 'Valid Name', 'offering_price': 1000}
    result = await api_client.patch('/offering/100000', json=update_request_budy)
    assert result.status_code == 404


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames='alt_price', argvalues=(-100, 3.141592, 1_000_001, None, 'String')
)
async def test_create_alt_price_validation_edge_cases(
    api_client, alt_price, create_client_fixture, create_offering_fixture
):
    client_id = create_client_fixture
    offering_id = create_offering_fixture
    create_request_body = {
        'client_id': client_id,
        'offering_id': offering_id,
        'alt_price': alt_price,
    }
    result = await api_client.post('/alt-price/', json=create_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_create_alt_price_already_exists(
    api_client, create_client_fixture, create_offering_fixture
):
    client_id = create_client_fixture
    offering_id = create_offering_fixture
    create_request_body = {'client_id': client_id, 'offering_id': offering_id, 'alt_price': 100}
    successfull_request = await api_client.post('/alt-price/', json=create_request_body)
    assert successfull_request.status_code == 200
    failed_result = await api_client.post('/alt-price/', json=create_request_body)
    assert failed_result.status_code == 409


@pytest.mark.integration
@pytest.mark.parametrize(argnames='id', argvalues=(-1, 3.141592, 1_000_001, 'string', None, dict))
async def test_read_alt_price_validation_edge_cases(api_client, id):
    result = await api_client.get(f'/alt-price/{id}')
    assert result.status_code == 422


@pytest.mark.integration
async def test_read_alt_price_not_found(api_client):
    result = await api_client.get('/alt-price/100000')
    assert result.status_code == 404


@pytest.mark.integration
@pytest.mark.parametrize(
    argnames='alt_price', argvalues=(-100, 3.141592, 1_000_001, None, 'String')
)
async def test_update_alt_price_validation_edge_cases(
    api_client, alt_price, create_alt_price_fixture
):
    id = create_alt_price_fixture
    create_request_body = {'alt_price': alt_price}
    result = await api_client.patch(f'/alt-price/{id}', json=create_request_body)
    assert result.status_code == 422


@pytest.mark.integration
async def test_update_alt_price_not_found(api_client):
    update_request_budy = {'offering_name': 'Valid Name', 'offering_price': 1000}
    result = await api_client.patch('/alt-price/100000', json=update_request_budy)
    assert result.status_code == 404

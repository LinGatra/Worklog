import pytest

from app.models.client import Client
from app.models.offering import Offering

pytestmark = pytest.mark.integration


async def _client(session, name='Test Client') -> Client:
    obj = Client(client_name=name)
    session.add(obj)
    await session.flush()
    return obj


async def _offering(session, name='Test Offering', price=100) -> Offering:
    obj = Offering(offering_name=name, offering_price=price)
    session.add(obj)
    await session.flush()
    return obj


def _sqlstate(exc_info) -> str | None:
    return getattr(exc_info.value.orig, 'sqlstate', None)


class TestClientCreate:
    # async def test_happy_path(self, session):
    #     client = await _client(session, name='Acme')
    #     assert client.client_id is not None
    #     assert client.client_name == 'Acme'

    # async def test_duplicate_client_name(self, session):
    #     await _client(session, name='Acme')
    #     session.add(Client(client_name='Acme'))

    #     with pytest.raises(IntegrityError) as exc_info:
    #         await session.flush()

    #     assert _sqlstate(exc_info) == '23505'
    pass

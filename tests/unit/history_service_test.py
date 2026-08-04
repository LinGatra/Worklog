from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exception_handling.domain_exceptions import (
    ForeignKeyViolation,
    NotFound,
    UniqueConstraintViolation,
)
from app.services.history import HistoryService

pytestmark = pytest.mark.unit


class DummyModel:
    pass


@pytest.fixture
def fake_repo():
    repo = AsyncMock()
    repo.model = DummyModel
    return repo


@pytest.fixture
def service(fake_repo):
    return HistoryService(repo=fake_repo)


# Тесты create
async def test_create_opens_transaction_and_returns_repo_result(service, fake_repo):
    fake_repo.create.return_value = 'created'
    session = MagicMock()

    result = await service.create(data={'name': 'x'}, session=session)

    assert result == 'created'
    session.begin.assert_called_once()
    fake_repo.create.assert_awaited_once_with(session=session, obj_in={'name': 'x'})


@pytest.mark.parametrize('exc_class', [UniqueConstraintViolation, ForeignKeyViolation])
async def test_create_propagates_exceptions(service, fake_repo, exc_class):
    fake_repo.create.side_effect = exc_class

    with pytest.raises(exc_class):
        await service.create('some_data', session=MagicMock())


async def test_create_logs_success(service, caplog):
    with caplog.at_level('INFO', logger='business_events'):
        await service.create(data={'name': 'x'}, session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].message == 'business_event_succeeded'
    assert events[0].model == 'DummyModel'
    assert events[0].action == 'create'


async def test_create_logs_failure(service, fake_repo, caplog):
    fake_repo.create.side_effect = ForeignKeyViolation

    with caplog.at_level('WARNING', logger='business_events'):
        with pytest.raises(ForeignKeyViolation):
            await service.create(data={'name': 'x'}, session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].error_type == 'ForeignKeyViolation'
    assert events[0].message == 'business_event_failed'


# тесты get_all
async def test_get_all_returns_repo_result(service, fake_repo):
    fake_repo.get_multi.return_value = {1: 'object_1', 2: 'object_2'}
    session = MagicMock()

    result = await service.get_all(session=session)

    assert result == {1: 'object_1', 2: 'object_2'}
    fake_repo.get_multi.assert_awaited_once_with(session=session)


@pytest.mark.parametrize('exc_class', [NotFound])
async def test_get_all_propagates_excepions(service, fake_repo, exc_class):
    fake_repo.get_multi.side_effect = exc_class

    with pytest.raises(exc_class):
        await service.get_all(session=MagicMock())


async def test_get_all_logs_success(service, caplog):
    with caplog.at_level('INFO', logger='business_events'):
        await service.get_all(session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].message == 'business_event_succeeded'
    assert events[0].model == 'DummyModel'
    assert events[0].action == 'get_all'


async def test_get_all_logs_failure(service, fake_repo, caplog):
    fake_repo.get_multi.side_effect = NotFound

    with caplog.at_level('WARNING', logger='business_events'):
        with pytest.raises(NotFound):
            await service.get_all(session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].error_type == 'NotFound'
    assert events[0].message == 'business_event_failed'


async def test_get_by_id_returns_repo_result(service, fake_repo):
    fake_repo.get.return_value = 'some object'
    session = MagicMock()

    result = await service.get_by_id(event_id=1, session=session)

    assert result == 'some object'
    fake_repo.get.assert_awaited_once_with(id=1, session=session)


@pytest.mark.parametrize('exc_class', [NotFound])
async def test_get_by_id_propagates_exceptions(service, fake_repo, exc_class):
    fake_repo.get.side_effect = exc_class

    with pytest.raises(exc_class):
        await service.get_by_id(event_id=1, session=MagicMock())


async def test_get_by_id_logs_success(service, caplog):
    with caplog.at_level('INFO', logger='business_events'):
        await service.get_by_id(event_id=1, session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].message == 'business_event_succeeded'
    assert events[0].model == 'DummyModel'
    assert events[0].action == 'get_by_id'


async def test_get_by_id_logs_failure(service, fake_repo, caplog):
    fake_repo.get.side_effect = NotFound

    with caplog.at_level('WARNING', logger='business_events'):
        with pytest.raises(NotFound):
            await service.get_by_id(event_id=1, session=MagicMock())

    events = [r for r in caplog.records if r.name == 'business_events']
    assert len(events) == 1
    assert events[0].error_type == 'NotFound'
    assert events[0].message == 'business_event_failed'

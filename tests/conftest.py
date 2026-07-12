from collections.abc import AsyncGenerator
from os import path

import pytest
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.models.alt_price import AltPrice  # noqa: F401
from app.models.client import Client  # noqa: F401
from app.models.history import History  # noqa: F401
from app.models.models_config import Base
from app.models.offering import Offering  # noqa: F401


@pytest.fixture(scope='session')
def postgres_container():
    with PostgresContainer('postgres:16-alpine') as container:
        yield container


def alembic_run_migrations(url: str):
    project_root = path.abspath(path.join(path.dirname(__file__), '..'))
    ini_path = path.join(project_root, 'alembic.ini')

    config = Config(ini_path)
    config.attributes['sqlalchemy_url'] = url

    command.upgrade(config, 'head')


@pytest.fixture(scope='session')
async def engine(postgres_container) -> AsyncGenerator[AsyncEngine]:
    alembic_url = postgres_container.get_connection_url().replace(
        'postgresql+psycopg2', 'postgresql+psycopg'
    )

    # testcontainers по умолчанию отдаёт psycopg2-URL, драйвер нужно подменить на asyncpg
    engine_url = postgres_container.get_connection_url().replace(
        'postgresql+psycopg2', 'postgresql+asyncpg'
    )
    engine = create_async_engine(engine_url, echo=False)

    alembic_run_migrations(url=alembic_url)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session

    # cleanup — truncate всех таблиц после теста, CASCADE из-за FK между Client/Offering/AltPrice/History
    async with engine.begin() as conn:
        tables = ', '.join(t.name for t in Base.metadata.sorted_tables)
        await conn.execute(text(f'TRUNCATE {tables} RESTART IDENTITY CASCADE'))

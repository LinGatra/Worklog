"""Инициализация движка и сессии. Используется postgres с asyncpg"""

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import config


async def init_db(app):
    engine: AsyncEngine = create_async_engine(config.SQLALCHEMY_DATABASE_URL, echo=False)
    app.state.engine = engine
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def close_db(app):
    try:
        await app.state.engine.dispose()
    except Exception as e:
        print(f'Error closing DB: {e}')

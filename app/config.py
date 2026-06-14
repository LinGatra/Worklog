from typing import Literal

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    ENVIRONMENT: Literal['dev', 'test', 'prod'] = 'dev'
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str

    # RUN
    APP_HOST: str
    APP_PORT: int

    # postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    def _build_url(self, driver: str) -> str:
        return str(
            MultiHostUrl.build(
                scheme=f'postgresql+{driver}',
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return self._build_url('asyncpg')

    @computed_field
    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        return self._build_url('psycopg')


config = Settings()  # type: ignore

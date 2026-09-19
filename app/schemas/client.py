from pydantic import Field

from app.schemas.schemas_config import Config


class ClientBase(Config):
    client_name: str = Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and puntuation symbols.',
    )


class ClientCreate(ClientBase):
    pass


class ClientCreateDB(ClientCreate):
    name_alias: str


class ClientRead(ClientCreate):
    id: int


class ClientUpdate(ClientBase):
    client_name: None | str = None  # type: ignore[assignment]

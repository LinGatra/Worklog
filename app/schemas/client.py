from typing import Annotated

from pydantic import Field, field_validator, model_validator

from app.schemas.schemas_config import Config

ClientName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and punctuation symbols.',
    ),
]


class ClientBase(Config):
    client_name: ClientName


class ClientCreate(ClientBase):
    pass


class ClientCreateDB(ClientCreate):
    name_alias: str


class ClientRead(ClientCreate):
    id: int


class ClientUpdate(Config):
    client_name: ClientName | None = None

    @field_validator('client_name')
    @classmethod
    def client_name_not_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('client_name cannot be null')
        return value


class ClientUpdateDB(ClientUpdate):
    name_alias: str | None = None

    @model_validator(mode='after')
    def alias_follows_name(self):
        if (self.client_name is None) != (self.name_alias is None):
            raise ValueError('client_name and name_alias must be provided together')
        return self

from pydantic import field_validator, model_validator

from app.exception_handling.domain_exceptions import DomainValidationException
from app.schemas.domain_types import ClientName, LimitedIntID
from app.schemas.schemas_config import Config


class ClientBase(Config):
    client_name: ClientName


class ClientCreate(ClientBase):
    pass


class ClientCreateDB(ClientBase):
    name_alias: str


class ClientRead(ClientBase):
    id: LimitedIntID


class ClientUpdate(Config):
    client_name: ClientName | None = None

    @field_validator('client_name')
    @classmethod
    def client_name_not_null(cls, value: str | None) -> str:
        if value is None:
            raise DomainValidationException('client_name cannot be null')
        return value


class ClientUpdateDB(ClientUpdate):
    name_alias: str | None = None

    @model_validator(mode='after')
    def alias_follows_name(self):
        if (self.client_name is None) != (self.name_alias is None):
            raise ValueError('client_name and name_alias must be provided together')
        return self

from typing import Annotated

from pydantic import Field, field_validator, model_validator

from app.schemas.schemas_config import Config

OfferingName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and puntuation symbols.',
    ),
]

OfferingPrice = Annotated[int, Field(ge=0, description='Price can not be less than zero')]


class OfferingBase(Config):
    offering_name: OfferingName
    offering_price: OfferingPrice


class OfferingCreate(OfferingBase):
    pass


class OfferingCreateDB(OfferingCreate):
    name_alias: str


class OfferingRead(OfferingCreate):
    id: int


class OfferingUpdate(Config):
    offering_name: OfferingName | None = None
    offering_price: OfferingPrice | None = None

    @field_validator('offering_name')
    @classmethod
    def offering_name_not_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('offering_name cannot be null')
        return value

    @field_validator('offering_price')
    @classmethod
    def offering_price_not_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('offering_price cannot be null')
        return value


class OfferingUpdateDB(OfferingUpdate):
    name_alias: str | None = None

    @model_validator(mode='after')
    def alias_follows_name(self):
        if (self.offering_name is None) != (self.name_alias is None):
            raise ValueError('offering_name and name_alias must be provided together')
        return self

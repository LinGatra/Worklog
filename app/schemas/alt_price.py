from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.schemas_config import Config

AltPrice = Annotated[int, Field(ge=0, description='Price can not be less than zero')]


class AltPriceBase(Config):
    alt_price: AltPrice


class AltPriceCreate(AltPriceBase):
    client_id: int
    offering_id: int


class AltPriceRead(AltPriceCreate):
    id: int


class AltPriceUpdate(Config):
    alt_price: AltPrice | None = None

    @field_validator('alt_price')
    @classmethod
    def alt_price_not_null(cls, value: int | None) -> int:
        if value is None:
            raise ValueError('alt_price cannot be null')
        return value

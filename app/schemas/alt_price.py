from pydantic import Field

from app.schemas.schemas_config import Config


class AltPriceBase(Config):
    alt_price: int = Field(ge=0, description='Price can not be less than zero')


class AltPriceCreate(AltPriceBase):
    client_id: int
    offering_id: int


class AltPriceRead(AltPriceCreate):
    alt_price_id: int


class AltPriceUpdate(AltPriceBase):
    alt_price: int | None = Field(ge=0, description='Price can not be less than zero', default=None)  # type: ignore[assignment]

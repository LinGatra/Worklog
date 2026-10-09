from pydantic import field_validator

from app.exception_handling.domain_exceptions import DomainValidationException
from app.schemas.domain_types import AltPrice, LimitedIntID
from app.schemas.schemas_config import Config


class AltPriceBase(Config):
    alt_price: AltPrice


class AltPriceCreate(AltPriceBase):
    client_id: LimitedIntID
    offering_id: LimitedIntID


class AltPriceRead(AltPriceCreate):
    id: LimitedIntID


class AltPriceUpdate(Config):
    alt_price: AltPrice | None = None

    @field_validator('alt_price')
    @classmethod
    def alt_price_not_null(cls, value: int | None) -> int:
        if value is None:
            raise DomainValidationException('alt_price cannot be null')
        return value

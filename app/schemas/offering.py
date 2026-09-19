from pydantic import Field

from app.schemas.schemas_config import Config


class OfferingBase(Config):
    offering_name: str = Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and puntuation symbols.',
    )
    offering_price: int = Field(ge=0, description='Price can not be less than zero')


class OfferingCreate(OfferingBase):
    pass


class OfferingCreateDB(OfferingCreate):
    name_alias: str


class OfferingRead(OfferingCreate):
    id: int


class OfferingUpdate(OfferingBase):
    offering_name: None | str = Field(  # type: ignore[assignment]
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and puntuation symbols.',
        default=None,
    )

    offering_price: None | int = Field(  # type: ignore[assignment]
        ge=0, description='Price can not be less than zero', default=None
    )

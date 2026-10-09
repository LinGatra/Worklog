from app.db.repositories.delete_strategy import HardDelete
from app.db.repositories.mixins import (
    CreateMixin,
    DeleteMixin,
    ReadMixin,
    UpdateMixin,
)
from app.models.alt_price import AltPrice
from app.schemas.alt_price import AltPriceCreate, AltPriceUpdate


class AltPriceRepository(
    CreateMixin[AltPrice, AltPriceCreate],
    ReadMixin[AltPrice],
    UpdateMixin[AltPrice, AltPriceUpdate],
    DeleteMixin[AltPrice],
):
    model = AltPrice
    deletion = HardDelete()


alt_price_repository = AltPriceRepository()

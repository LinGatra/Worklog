from app.db.base_repository import BaseRepository
from app.models.alt_price import AltPrice
from app.schemas.alt_price import AltPriceCreate, AltPriceUpdate
from app.services.base_service import BaseService


class AltPriceService(BaseService[AltPrice, AltPriceCreate, AltPriceUpdate]):
    pass


alt_price_repository = BaseRepository(AltPrice)
alt_price_service = AltPriceService(repo=alt_price_repository)

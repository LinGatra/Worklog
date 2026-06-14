from app.db.base_repository import BaseRepository
from app.models.offering import Offering
from app.schemas.offering import OfferingCreate, OfferingUpdate
from app.services.base_service import BaseService


class OfferingService(BaseService[Offering, OfferingCreate, OfferingUpdate]):
    pass


offering_repository = BaseRepository(Offering)
offering_service = OfferingService(repo=offering_repository)

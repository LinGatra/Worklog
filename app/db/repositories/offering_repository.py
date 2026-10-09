from app.db.repositories.delete_strategy import SoftDelete
from app.db.repositories.mixins import (
    CreateMixin,
    DeleteMixin,
    DeletionAwareReadMixin,
    DeletionAwareUpdateMixin,
)
from app.models.offering import Offering
from app.schemas.offering import OfferingCreateDB, OfferingUpdateDB


class OfferingRepository(
    CreateMixin[Offering, OfferingCreateDB],
    DeletionAwareReadMixin[Offering],
    DeletionAwareUpdateMixin[Offering, OfferingUpdateDB],
    DeleteMixin[Offering],
):
    model = Offering
    deletion = SoftDelete()


offering_repository = OfferingRepository()

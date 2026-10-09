from app.schemas.domain_types import LimitedIntID, OfferingPrice
from app.schemas.schemas_config import Config


class HistoryDetailsCreate(Config):
    event_id: LimitedIntID
    offering_id: LimitedIntID
    offering_price: OfferingPrice


class HistoryDetailsRead(Config):
    id: LimitedIntID

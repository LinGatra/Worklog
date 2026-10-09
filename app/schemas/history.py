from datetime import datetime

from app.schemas.domain_types import LimitedIntID
from app.schemas.schemas_config import Config


class HistoryCreate(Config):
    client_id: LimitedIntID
    final_price: int


class HistoryRead(HistoryCreate):
    id: LimitedIntID
    created_at: datetime

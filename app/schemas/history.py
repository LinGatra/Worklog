from datetime import datetime

from app.schemas.schemas_config import Config


class HistoryCreate(Config):
    client_id: int
    offering_id: int


class HistoryRead(HistoryCreate):
    id: int
    price: int
    created_at: datetime

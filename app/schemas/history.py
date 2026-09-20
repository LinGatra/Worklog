from datetime import datetime

from app.schemas.schemas_config import Config


class HistoryCreate(Config):
    client_id: int
    final_price: int


class HistoryRead(HistoryCreate):
    id: int
    created_at: datetime

from app.schemas.schemas_config import Config


class HistoryDetailsCreate(Config):
    event_id: int
    offering_id: int
    offering_price: int


class HistoryDetailsRead(HistoryDetailsCreate):
    id: int

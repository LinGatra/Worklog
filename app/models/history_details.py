from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.history import History
from app.models.models_config import Base
from app.models.offering import Offering


class HistoryDetails(Base):
    __tablename__ = 'history_details'

    detail_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(History.event_id), nullable=False)
    offering_id: Mapped[int] = mapped_column(ForeignKey(Offering.offering_id), nullable=False)
    offering_price: Mapped[int] = mapped_column(Integer, nullable=False)

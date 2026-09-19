from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.history import History
from app.models.models_config import Base
from app.models.offering import Offering


class HistoryDetails(Base):
    __tablename__ = 'history_details'

    id: Mapped[int] = mapped_column('detail_id', Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(History.id), nullable=False)
    offering_id: Mapped[int] = mapped_column(ForeignKey(Offering.id), nullable=False)
    offering_price: Mapped[int] = mapped_column(Integer, nullable=False)

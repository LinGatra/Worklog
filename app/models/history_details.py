from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base
from app.models.history import History
from app.models.offering import Offering


class HistoryDetails(Base):
    __tablename__ = 'history_details'

    id: Mapped[int] = mapped_column('detail_id', Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(History.id), nullable=False)
    offering_id: Mapped[int] = mapped_column(ForeignKey(Offering.id), nullable=False)
    offering_price: Mapped[int] = mapped_column(Integer, nullable=False)

    event: Mapped[History] = relationship('History', back_populates='details')

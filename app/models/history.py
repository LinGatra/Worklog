from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base
from app.models.client import Client

if TYPE_CHECKING:
    from app.models.history_details import HistoryDetails


class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column('event_id', Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey(Client.id), nullable=False)
    final_price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    details: Mapped[list[HistoryDetails]] = relationship('HistoryDetails', back_populates='event')

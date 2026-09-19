from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.client import Client
from app.models.models_config import Base


class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column('event_id', Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey(Client.id), nullable=False)
    final_price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

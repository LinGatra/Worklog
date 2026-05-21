from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.client import Client
from app.models.models_config import Base
from app.models.service import Service


class History(Base):
    __tablename__ = 'history'

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey(Client.client_id), nullable=False)
    client_name: Mapped[str] = mapped_column(ForeignKey(Client.client_name), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey(Service.service_id), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

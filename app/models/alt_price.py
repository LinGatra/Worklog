from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.client import Client
from app.models.models_config import Base
from app.models.service import Service


class Alt_price(Base):
    __tablename__ = 'alt_price'

    alt_price_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey(Client.client_id), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey(Service.service_id), nullable=False)
    alt_price: Mapped[int] = mapped_column(Integer, nullable=False)

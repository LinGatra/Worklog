from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.models_config import Base


class Service(Base):
    __tablename__ = 'service'

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    service_price: Mapped[int] = mapped_column(Integer, nullable=False)

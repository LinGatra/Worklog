from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.models_config import Base


class Client(Base):
    __tablename__ = 'client'

    client_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

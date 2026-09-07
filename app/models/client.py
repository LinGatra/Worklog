from sqlalchemy import Boolean, CheckConstraint, Integer, String, false as sa_false
from sqlalchemy.orm import Mapped, mapped_column

from app.models.models_config import Base


class Client(Base):
    __tablename__ = 'client'

    client_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_alias: Mapped[str] = mapped_column(String, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa_false())

    __table_args__ = (
        CheckConstraint('client_id >= 1', name='id_can_not_be_less_than_1'),
        CheckConstraint('length(client_name) >= 1', name='name_can_not_be_empty'),
    )

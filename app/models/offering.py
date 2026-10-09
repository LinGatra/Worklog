from sqlalchemy import Boolean, CheckConstraint, Integer, String, false as sa_false
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import Base


class Offering(Base):
    __tablename__ = 'offering'

    id: Mapped[int] = mapped_column('offering_id', Integer, primary_key=True)
    offering_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_alias: Mapped[str] = mapped_column(String, nullable=False)
    offering_price: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa_false())

    __table_args__ = (
        CheckConstraint('offering_price >= 0', name='price_can_not_be_negative'),
        CheckConstraint('length(offering_name) >= 1', name='name_can_not_be_empty'),
    )

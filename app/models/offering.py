from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.models_config import Base


class Offering(Base):
    __tablename__ = 'offering'

    offering_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offering_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    offering_price: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('offering_price >= 0', name='ck_offering_price_non_negative'),
        CheckConstraint('lenght(offering_name) >= 1', name='name_not_null'),
    )

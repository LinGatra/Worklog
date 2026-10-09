from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import Base
from app.models.client import Client
from app.models.offering import Offering


class AltPrice(Base):
    __tablename__ = 'alt_price'

    id: Mapped[int] = mapped_column('alt_price_id', Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey(Client.id), nullable=False)
    offering_id: Mapped[int] = mapped_column(ForeignKey(Offering.id), nullable=False)
    alt_price: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('client_id', 'offering_id', name='uq_client_offering_price'),
        CheckConstraint('alt_price >= 0', name='ck_alt_price_non_negative'),
    )

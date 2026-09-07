from typing import Any

from sqlalchemy import func, insert, literal, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception_handling.domain_exceptions import (
    CheckConstraintViolation,
    ForeignKeyViolation,
    NotFound,
)
from app.models.alt_price import AltPrice
from app.models.history import History
from app.models.offering import Offering
from app.schemas.history import HistoryCreate


class HistoryRepository:
    def __init__(self):
        self.model = History

    async def get(self, session: AsyncSession, id: Any) -> History | None:
        result = await session.get(History, id)
        if result is None:
            raise NotFound
        else:
            return result

    # Пагинация через `limit / offset`. Возможно, стоит пересмотреть в будущем, и вместо offset использовать id
    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        statement = select(History).offset(skip).limit(limit)
        result = await session.execute(statement)
        if result:
            return result.scalars().all()
        else:
            raise NotFound

    async def create(self, session: AsyncSession, data: HistoryCreate) -> History:
        client_id = data.client_id
        offering_id = data.offering_id
        select_stmt = (
            select(
                func.coalesce(AltPrice.alt_price, Offering.offering_price).label('price'),
                literal(client_id).label('client_id'),
                Offering.offering_id,
            )
            .select_from(Offering)
            .join(
                AltPrice,
                (AltPrice.offering_id == Offering.offering_id) & (AltPrice.client_id == client_id),
                isouter=True,
            )
            .where(Offering.offering_id == offering_id)
        )

        insert_stmt = (
            insert(History)
            .from_select(['price', 'client_id', 'offering_id'], select_stmt)
            .returning(History)
        )

        try:
            result = await session.execute(insert_stmt)
            row = result.scalar_one()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, 'sqlstate', None)
            match sqlstate:
                case '23514':
                    raise CheckConstraintViolation from e
                case '23503':
                    raise ForeignKeyViolation from e
            raise

        except NoResultFound as e:
            raise NotFound from e

        else:
            await session.flush()
            return row


history_repository = HistoryRepository()

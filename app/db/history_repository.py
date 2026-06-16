from typing import Any

from sqlalchemy import func, insert, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alt_price import AltPrice
from app.models.history import History
from app.models.offering import Offering


class HistoryRepository:
    def __init__(self):
        self.model = History

    async def get(self, session: AsyncSession, id: Any) -> History | None:
        return await session.get(History, id)

    # Пагинация через `limit / offset`. Возможно, стоит пересмотреть в будущем, и вместо offset использовать id
    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        statement = select(History).offset(skip).limit(limit)
        result = await session.execute(statement)
        return result.scalars().all()

    async def create(self, session: AsyncSession, client_id: int, offering_id: int) -> History:

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

        result = await session.execute(insert_stmt)
        await session.flush()

        return result.scalar_one()


history_repository = HistoryRepository()

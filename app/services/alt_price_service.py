from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.alt_price_repository import alt_price_repository
from app.schemas.alt_price import AltPriceCreate, AltPriceRead, AltPriceUpdate


class AltPriceService:
    async def create(self, *, session: AsyncSession, data: AltPriceCreate) -> AltPriceRead:
        async with session.begin():
            result = await alt_price_repository.create(session=session, data=data)
            return AltPriceRead.model_validate(result)

    async def get(self, *, session: AsyncSession, id: int) -> AltPriceRead | None:
        async with session.begin():
            result = await alt_price_repository.get(session=session, id=id)
            return AltPriceRead.model_validate(result) if result else None

    async def get_page(self, *, session: AsyncSession) -> Sequence[AltPriceRead]:
        async with session.begin():
            result = await alt_price_repository.get_page(session=session)
            return [AltPriceRead.model_validate(alt_price) for alt_price in result]

    async def update(self, *, session: AsyncSession, id: int, data: AltPriceUpdate) -> AltPriceRead:
        async with session.begin():
            result = await alt_price_repository.update(session=session, id=id, data=data)
            return AltPriceRead.model_validate(result)

    async def delete(self, *, session: AsyncSession, id: int) -> None:
        async with session.begin():
            await alt_price_repository.delete(session=session, id=id)


alt_price_service = AltPriceService()

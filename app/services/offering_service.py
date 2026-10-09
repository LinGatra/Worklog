from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.offering_repository import offering_repository
from app.limitations import make_alias, normalize_for_ui
from app.schemas.offering import (
    OfferingCreate,
    OfferingCreateDB,
    OfferingRead,
    OfferingUpdate,
    OfferingUpdateDB,
)


class OfferingService:
    async def create(self, *, session: AsyncSession, data: OfferingCreate) -> OfferingRead:
        normalized_name = normalize_for_ui(str_in=data.offering_name, field_name='offering_name')
        name_alias = make_alias(str_in=data.offering_name, field_name='offering_name')
        offering_price = data.offering_price

        data = OfferingCreateDB(
            offering_name=normalized_name, name_alias=name_alias, offering_price=offering_price
        )
        async with session.begin():
            result = await offering_repository.create(session=session, data=data)
            return OfferingRead.model_validate(result)

    async def get(self, *, session: AsyncSession, id: int) -> OfferingRead | None:
        async with session.begin():
            result = await offering_repository.get(session=session, id=id)
            return OfferingRead.model_validate(result) if result else None

    async def get_page(self, *, session: AsyncSession) -> Sequence[OfferingRead]:
        async with session.begin():
            result = await offering_repository.get_page(session=session)
            return [OfferingRead.model_validate(offering) for offering in result]

    async def update(self, *, session: AsyncSession, id: int, data: OfferingUpdate) -> OfferingRead:
        values = data.model_dump(exclude_unset=True)

        if data.offering_name is not None:
            values['offering_name'] = normalize_for_ui(
                str_in=data.offering_name, field_name='offering_name'
            )
            values['name_alias'] = make_alias(str_in=data.offering_name, field_name='offering_name')

        db_data = OfferingUpdateDB(**values)

        async with session.begin():
            result = await offering_repository.update(session=session, id=id, data=db_data)
            return OfferingRead.model_validate(result)

    async def delete(self, *, session: AsyncSession, id: int) -> None:
        async with session.begin():
            await offering_repository.delete(session=session, id=id)


offering_service = OfferingService()

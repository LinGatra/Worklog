from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.client_repository import client_repository
from app.exception_handling.domain_exceptions import NotFound
from app.limitations import make_alias, normalize_for_ui
from app.schemas.client import (
    ClientCreate,
    ClientCreateDB,
    ClientRead,
    ClientUpdate,
    ClientUpdateDB,
)


class ClientService:
    async def create(self, *, session: AsyncSession, data: ClientCreate) -> ClientRead:
        normalized_name = normalize_for_ui(str_in=data.client_name, field_name='client_name')
        name_alias = make_alias(str_in=data.client_name, field_name='client_name')

        db_data = ClientCreateDB(client_name=normalized_name, name_alias=name_alias)
        async with session.begin():
            result = await client_repository.create(session=session, data=db_data)
            return ClientRead.model_validate(result)

    async def get(self, *, session: AsyncSession, id: int) -> ClientRead:
        async with session.begin():
            result = await client_repository.get(session=session, id=id)
            if result:
                return ClientRead.model_validate(result)
            else:
                raise NotFound

    async def get_page(self, *, session: AsyncSession) -> Sequence[ClientRead]:
        async with session.begin():
            result = await client_repository.get_page(session=session)
            return [ClientRead.model_validate(client) for client in result]

    async def update(self, *, session: AsyncSession, id: int, data: ClientUpdate) -> ClientRead:
        values = data.model_dump(exclude_unset=True)

        if data.client_name:
            values['client_name'] = normalize_for_ui(
                str_in=data.client_name, field_name='client_name'
            )
            values['name_alias'] = make_alias(str_in=data.client_name, field_name='client_name')

        db_data = ClientUpdateDB(**values)

        async with session.begin():
            result = await client_repository.update(session=session, id=id, data=db_data)
            return ClientRead.model_validate(result)

    async def delete(self, *, session: AsyncSession, id: int) -> None:
        async with session.begin():
            await client_repository.delete(session=session, id=id)


client_service = ClientService()

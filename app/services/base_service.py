from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.app_logging.business_log import log_business_event
from app.db.base_repository import BaseRepository


class BaseService[ModelType, CreateSchemaType, UpdateSchemaType]:
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @log_business_event(action='create')
    async def create(self, data: CreateSchemaType, session: AsyncSession) -> ModelType:
        async with session.begin():
            new_object = await self.repo.create(session=session, obj_in=data)
            return new_object

    @log_business_event(action='get_all')
    async def get_all(self, session: AsyncSession) -> Sequence[ModelType] | None:
        result = await self.repo.get_multi(session=session)
        return result

    @log_business_event(action='get_by_id')
    async def get_by_id(self, id, session: AsyncSession) -> ModelType | None:
        result = await self.repo.get(id=id, session=session)
        return result

    @log_business_event(action='update')
    async def update(self, id, data: UpdateSchemaType, session: AsyncSession) -> ModelType | None:
        async with session.begin():
            db_obj = await self.get_by_id(id=id, session=session)
            updated_object = await self.repo.update(session=session, db_obj=db_obj, obj_in=data)

            return updated_object

    @log_business_event(action='delete')
    async def delete(self, id, session: AsyncSession) -> ModelType | None:
        async with session.begin():
            deleted_object = await self.repo.remove(id=id, session=session)
            return deleted_object

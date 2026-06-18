from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_repository import BaseRepository


class BaseService[ModelType, CreateSchemaType, UpdateSchemaType]:
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    async def create(self, data: CreateSchemaType, session: AsyncSession) -> ModelType:
        new_object = await self.repo.create(session=session, obj_in=data)
        await session.commit()
        return new_object

    async def get_all(self, session: AsyncSession) -> Sequence[ModelType] | None:
        return await self.repo.get_multi(session=session)

    async def get_by_id(self, id, session: AsyncSession) -> ModelType | None:
        return await self.repo.get(id=id, session=session)

    async def update(self, id, data: UpdateSchemaType, session: AsyncSession) -> ModelType | None:
        db_obj = await self.get_by_id(id=id, session=session)
        if db_obj is None:
            return None

        updated_object = await self.repo.update(session=session, db_obj=db_obj, obj_in=data)

        await session.commit()
        return updated_object

    async def delete(self, id, session: AsyncSession) -> ModelType | None:

        deleted_object = await self.repo.remove(id=id, session=session)
        await session.commit()

        return deleted_object

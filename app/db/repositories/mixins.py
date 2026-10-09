from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from app.db.repositories.delete_strategy import DeletedFilter, DeletionStrategy
from app.exception_handling.domain_exceptions import NotFound
from app.exception_handling.mapping import map_integrity_error


class HasId(Protocol):
    id: Mapped[int]


class BaseRepository[ModelType: HasId]:
    model: type[ModelType]


class DeletionAwareRepository[ModelType: HasId](BaseRepository[ModelType]):
    deletion: DeletionStrategy


class CreateMixin[ModelType: HasId, CreateSchemaType: BaseModel](BaseRepository[ModelType]):
    async def create(self, *, session: AsyncSession, data: CreateSchemaType) -> ModelType:
        db_obj = self.model(**data.model_dump())
        session.add(db_obj)
        try:
            await session.flush()
        except IntegrityError as e:
            raise map_integrity_error(e) from e
        return db_obj


class ReadMixin[ModelType: HasId](BaseRepository[ModelType]):
    async def get(self, *, session: AsyncSession, id: int) -> ModelType | None:
        result = (
            await session.execute(select(self.model).where(self.model.id == id))
        ).scalar_one_or_none()

        if result is None:
            raise NotFound

    async def get_page(self, *, session: AsyncSession) -> Sequence[ModelType]:
        return (await session.execute(select(self.model))).scalars().all()


class DeletionAwareReadMixin[ModelType: HasId](DeletionAwareRepository[ModelType]):
    async def get(
        self, *, session: AsyncSession, id: int, deleted: DeletedFilter = DeletedFilter.EXCLUDE
    ) -> ModelType | None:

        stmt = select(self.model).where(self.model.id == id)
        stmt = self.deletion.apply_read_filter(stmt=stmt, model=self.model, mode=deleted)
        result = (await session.execute(stmt)).scalar_one_or_none()

        if result is None:
            raise NotFound

    async def get_page(
        self, *, session: AsyncSession, deleted: DeletedFilter = DeletedFilter.EXCLUDE
    ) -> Sequence[ModelType]:
        stmt = self.deletion.apply_read_filter(
            stmt=select(self.model), model=self.model, mode=deleted
        )
        return (await session.execute(stmt)).scalars().all()


class UpdateMixin[ModelType: HasId, UpdateSchemaType: BaseModel](BaseRepository[ModelType]):
    def _select_for_update(self, id: int) -> Select[tuple[ModelType]]:
        return select(self.model).where(self.model.id == id).with_for_update()

    async def update(self, *, session: AsyncSession, id: int, data: UpdateSchemaType) -> ModelType:
        db_obj = (await session.execute(self._select_for_update(id))).scalar_one_or_none()
        if db_obj is None:
            raise NotFound
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        try:
            await session.flush()

        except IntegrityError as e:
            raise map_integrity_error(e) from e
        return db_obj


class DeletionAwareUpdateMixin[ModelType: HasId, UpdateSchemaType: BaseModel](
    DeletionAwareRepository[ModelType], UpdateMixin[ModelType, UpdateSchemaType]
):
    def _select_for_update(self, id: int) -> Select[tuple[ModelType]]:
        return self.deletion.apply_mutation_guard(
            stmt=super()._select_for_update(id), model=self.model
        )


class DeleteMixin[ModelType: HasId](DeletionAwareRepository[ModelType]):
    async def delete(self, *, session: AsyncSession, id: int) -> None:
        if await self.deletion.delete(session=session, model=self.model, id=id) is None:
            raise NotFound

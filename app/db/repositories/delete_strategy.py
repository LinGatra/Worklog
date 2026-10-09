from enum import Enum
from typing import Protocol

from sqlalchemy import Select, delete as sa_delete, false, update
from sqlalchemy.ext.asyncio import AsyncSession


class DeletedFilter(Enum):
    EXCLUDE = 'exclude'
    ONLY = 'only'
    ANY = 'any'


class DeletionStrategy(Protocol):
    def apply_read_filter(self, *, stmt: Select, model, mode: DeletedFilter) -> Select: ...
    def apply_mutation_guard(self, *, stmt: Select, model) -> Select: ...
    async def delete(self, *, session: AsyncSession, model, id: int) -> bool: ...


class SoftDelete:
    def apply_read_filter(self, *, stmt: Select, model, mode: DeletedFilter) -> Select:
        match mode:
            case DeletedFilter.EXCLUDE:
                return stmt.where(model.is_deleted.is_(False))
            case DeletedFilter.ONLY:
                return stmt.where(model.is_deleted.is_(True))
            case DeletedFilter.ANY:
                return stmt

    def apply_mutation_guard(self, *, stmt: Select, model) -> Select:
        return stmt.where(model.is_deleted.is_(False))

    async def delete(self, *, session: AsyncSession, model, id: int) -> bool:
        result = await session.execute(
            update(model)
            .where(model.id == id, model.is_deleted.is_(False))
            .values(is_deleted=True)
            .returning(model.id)
        )
        return result.scalar_one_or_none() is not None


class HardDelete:
    def apply_read_filter(self, *, stmt: Select, model, mode: DeletedFilter) -> Select:
        if mode is DeletedFilter.ONLY:
            return stmt.where(false())
        return stmt

    def apply_mutation_guard(self, *, stmt: Select, model) -> Select:
        return stmt

    async def delete(self, *, session: AsyncSession, model, id: int) -> bool:
        result = await session.execute(sa_delete(model).where(model.id == id).returning(model.id))
        return result.scalar_one_or_none() is not None

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception_handling.domain_exceptions import (
    ForeignKeyViolation,
    NotFound,
    NotNullViolation,
    UniqueConstraintViolation,
)


class BaseRepository[ModelType, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> ModelType | None:
        result = await session.get(self.model, id)
        if result is None:
            raise NotFound
        else:
            return result

    # Пагинация через `limit / offset`. Возможно, стоит пересмотреть в будущем, и вместо offset использовать id
    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.execute(statement)

        if result:
            return result.scalars().all()
        else:
            raise NotFound

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)

        session.add(db_obj)

        try:
            await session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, 'sqlstate', None)
            match sqlstate:
                case '23505':
                    raise UniqueConstraintViolation from e
                case '23503':
                    raise ForeignKeyViolation from e
                case _:
                    raise
        else:
            return db_obj

    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)

        try:
            await session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, 'sqlstate', None)
            match sqlstate:
                case '23502':
                    raise NotNullViolation from e
                case '23503':
                    raise ForeignKeyViolation from e
                case '23505':
                    raise UniqueConstraintViolation from e
                case _:
                    raise
        else:
            return db_obj

    async def remove(self, session: AsyncSession, id: Any) -> ModelType | None:
        db_obj = await session.get(self.model, id)
        if db_obj:
            await session.delete(db_obj)
            try:
                await session.flush()
            except IntegrityError as e:
                sqlstate = getattr(e.orig, 'sqlstate', None)
                match sqlstate:
                    case '23503':
                        raise ForeignKeyViolation from e
                    case _:
                        raise
            else:
                return db_obj
        else:
            raise NotFound

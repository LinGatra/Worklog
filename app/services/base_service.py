from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.app_logging.business_log import log_business_event
from app.db.base_repository import BaseRepository
from app.exception_handling.domain_exceptions import (
    ForeignKeyViolation,
    NotFound,
    UniqueConstraintViolation,
)
from app.exception_handling.http_exception_handling import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)


class BaseService[ModelType, CreateSchemaType, UpdateSchemaType]:
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @log_business_event(action='create')
    async def create(self, data: CreateSchemaType, session: AsyncSession) -> ModelType:
        try:
            async with session.begin():
                new_object = await self.repo.create(session=session, obj_in=data)

        except ForeignKeyViolation as e:
            raise BadRequestException from e
        except UniqueConstraintViolation as e:
            raise ConflictException from e

        else:
            return new_object

    @log_business_event(action='get_all')
    async def get_all(self, session: AsyncSession) -> Sequence[ModelType] | None:
        try:
            result = await self.repo.get_multi(session=session)
        except NotFound as e:
            raise NotFoundException from e
        else:
            return result

    @log_business_event(action='get_by_id')
    async def get_by_id(self, id, session: AsyncSession) -> ModelType | None:
        try:
            result = await self.repo.get(id=id, session=session)
        except NotFound as e:
            raise NotFoundException from e
        else:
            return result

    @log_business_event(action='update')
    async def update(self, id, data: UpdateSchemaType, session: AsyncSession) -> ModelType | None:
        db_obj = await self.get_by_id(id=id, session=session)

        try:
            async with session.begin():
                updated_object = await self.repo.update(session=session, db_obj=db_obj, obj_in=data)

        except ForeignKeyViolation as e:
            raise BadRequestException from e

        else:
            return updated_object

    @log_business_event(action='delete')
    async def delete(self, id, session: AsyncSession) -> ModelType | None:
        try:
            async with session.begin():
                deleted_object = await self.repo.remove(id=id, session=session)

        except ForeignKeyViolation as e:
            raise BadRequestException from e
        except NotFound as e:
            raise NotFoundException from e

        else:
            return deleted_object

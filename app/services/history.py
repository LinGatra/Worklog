from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.app_logging.business_log import log_business_event
from app.db.history_repository import history_repository
from app.exception_handling.domain_exceptions import NotFound
from app.exception_handling.http_exception_handling import NotFoundException
from app.models.history import History
from app.schemas.history import HistoryCreate


class HistoryService:
    def __init__(self):
        self.repo = history_repository

    @log_business_event(action='get_by_id')
    async def get_by_id(self, event_id: int, session: AsyncSession) -> History | None:
        try:
            result = await self.repo.get(id=event_id, session=session)
        except NotFound as e:
            raise NotFoundException from e
        else:
            return result

    @log_business_event(action='get_all')
    async def get_all(self, session: AsyncSession) -> Sequence[History] | None:
        try:
            result = await self.repo.get_multi(session=session)
        except NotFound as e:
            raise NotFoundException from e
        else:
            return result

    async def create(self, data: HistoryCreate, session: AsyncSession) -> History:
        async with session.begin():
            return await self.repo.create(session=session, data=data)


history_service = HistoryService()

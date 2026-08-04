from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.app_logging.business_log import log_business_event
from app.db.history_repository import history_repository
from app.models.history import History
from app.schemas.history import HistoryCreate


class HistoryService:
    def __init__(self, repo):
        self.repo = repo

    @log_business_event(action='get_by_id')
    async def get_by_id(self, event_id: int, session: AsyncSession) -> History | None:
        result = await self.repo.get(id=event_id, session=session)
        return result

    @log_business_event(action='get_all')
    async def get_all(self, session: AsyncSession) -> Sequence[History] | None:
        result = await self.repo.get_multi(session=session)
        return result

    @log_business_event(action='create')
    async def create(self, data: HistoryCreate, session: AsyncSession) -> History:
        async with session.begin():
            result = await self.repo.create(session=session, obj_in=data)
            return result


history_service = HistoryService(repo=history_repository)

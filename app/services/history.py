from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.history_repository import history_repository
from app.models.history import History
from app.schemas.history import HistoryCreate


class HistoryService:
    def __init__(self):
        self.repo = history_repository

    async def get_by_id(self, event_id: int, session: AsyncSession) -> History | None:
        return await self.repo.get(id=event_id, session=session)

    async def get_all(self, session: AsyncSession) -> Sequence[History] | None:
        return await self.repo.get_multi(session=session)

    async def create(self, data: HistoryCreate, session: AsyncSession) -> History:
        async with session.begin():
            return await self.repo.create(session=session, data=data)


history_service = HistoryService()

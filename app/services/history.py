from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.history_repository import history_repository
from app.models.history import History


class HistoryService:
    def __init__(self):
        self.repo = history_repository

    async def get_by_id(self, event_id: int, session: AsyncSession) -> History | None:
        return await self.repo.get(id=id, session=session)

    async def get_all(self, session: AsyncSession) -> Sequence[History] | None:
        return await self.repo.get_multi(session=session)

    async def create(self, client_id: int, offering_id: int, session: AsyncSession) -> History:
        new_event = await self.repo.create(
            session=session, client_id=client_id, offering_id=offering_id
        )
        await session.commit()
        return new_event


history_service = HistoryService()

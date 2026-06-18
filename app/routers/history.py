from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.history import HistoryCreate, HistoryRead
from app.services.history import history_service

history: APIRouter = APIRouter(prefix='/history', tags=['History'])


@history.get('/', response_model=list[HistoryRead])
async def get_all_history(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await history_service.get_all(session=session)


@history.get('/{id}', response_model=HistoryRead)
async def get_by_id(session: Annotated[AsyncSession, Depends(db_connect)], id: int):
    return await history_service.get_by_id(session=session, event_id=id)


@history.post('/', response_model=HistoryRead)
async def create_history(
    entry: HistoryCreate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await history_service.create(session=session, data=entry)

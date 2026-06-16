from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.history import HistoryRead
from app.services.history import history_service

history: APIRouter = APIRouter(prefix='/history', tags=['History'])


@history.get('/', response_model=list[HistoryRead])
async def get_all_history(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await history_service.get_all(session=session)


@history.get('/{id}', response_model=HistoryRead)
async def get_by_id(session: Annotated[AsyncSession, Depends(db_connect)], id: int):
    return await history_service.get_by_id(session=session, event_id=id)


@history.post('/{client_id}/{offering_id}')
async def create_history(
    session: Annotated[AsyncSession, Depends(db_connect)], client_id: int, offering_id: int
):
    return await history_service.create(
        session=session, client_id=client_id, offering_id=offering_id
    )

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.offering import OfferingCreate, OfferingRead, OfferingUpdate
from app.services.offering import offering_service

offering: APIRouter = APIRouter(prefix='/offering')


@offering.get('/', response_model=list[OfferingRead])
async def get_all_offerings(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await offering_service.get_all(session=session)


@offering.get('/{id}', response_model=OfferingRead)
async def get_offering_by_id(session: Annotated[AsyncSession, Depends(db_connect)], id: int):
    return await offering_service.get_by_id(id=id, session=session)


@offering.post('/', response_model=OfferingRead)
async def create_offering(
    data: OfferingCreate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await offering_service.create(data=data, session=session)


@offering.patch('/{id}', response_model=OfferingRead)
async def update_offering(
    id: int, data: OfferingUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await offering_service.update(id=id, data=data, session=session)


@offering.delete('/{id}')
async def delete_offering(id: int, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await offering_service.delete(id=id, session=session)

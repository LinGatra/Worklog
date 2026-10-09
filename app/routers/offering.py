from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.domain_types import LimitedIntID
from app.schemas.offering import OfferingCreate, OfferingRead, OfferingUpdate
from app.services.offering_service import offering_service

offering: APIRouter = APIRouter(prefix='/offering', tags=['Offering'])


@offering.get('/', response_model=list[OfferingRead])
async def get_page(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await offering_service.get_page(session=session)


@offering.get('/{id}', response_model=OfferingRead)
async def get(session: Annotated[AsyncSession, Depends(db_connect)], id: LimitedIntID):
    return await offering_service.get(id=id, session=session)


@offering.post('/', response_model=OfferingRead)
async def create(data: OfferingCreate, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await offering_service.create(data=data, session=session)


@offering.patch('/{id}', response_model=OfferingRead)
async def update(
    id: LimitedIntID, data: OfferingUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await offering_service.update(id=id, data=data, session=session)


@offering.delete('/{id}')
async def delete(id: LimitedIntID, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await offering_service.delete(id=id, session=session)

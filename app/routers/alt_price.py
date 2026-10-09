from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.alt_price import AltPriceCreate, AltPriceRead, AltPriceUpdate
from app.schemas.domain_types import LimitedIntID
from app.services.alt_price_service import alt_price_service

alt_price: APIRouter = APIRouter(prefix='/alt-price', tags=['Alt Price'])


@alt_price.get('/', response_model=list[AltPriceRead])
async def get_page(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await alt_price_service.get_page(session=session)


@alt_price.get('/{id}', response_model=AltPriceRead)
async def get(session: Annotated[AsyncSession, Depends(db_connect)], id: LimitedIntID):
    return await alt_price_service.get(id=id, session=session)


@alt_price.post('/', response_model=AltPriceRead)
async def create(data: AltPriceCreate, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await alt_price_service.create(data=data, session=session)


@alt_price.patch('/{id}', response_model=AltPriceRead)
async def update(
    id: LimitedIntID, data: AltPriceUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await alt_price_service.update(id=id, data=data, session=session)


@alt_price.delete('/{id}')
async def delete(id: LimitedIntID, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await alt_price_service.delete(id=id, session=session)

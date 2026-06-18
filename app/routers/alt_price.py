from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.alt_price import AltPriceCreate, AltPriceRead, AltPriceUpdate
from app.services.alt_price import alt_price_service

alt_price: APIRouter = APIRouter(prefix='/alt-price', tags=['Alt Price'])


@alt_price.get('/', response_model=list[AltPriceRead])
async def get_all_alt_prices(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await alt_price_service.get_all(session=session)


@alt_price.get('/{id}', response_model=AltPriceRead)
async def get_alt_price_by_id(session: Annotated[AsyncSession, Depends(db_connect)], id: int):
    return await alt_price_service.get_by_id(id=id, session=session)


@alt_price.post('/', response_model=AltPriceRead)
async def create_alt_price(
    data: AltPriceCreate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await alt_price_service.create(data=data, session=session)


@alt_price.patch('/{id}', response_model=AltPriceRead)
async def update_alt_price(
    id: int, data: AltPriceUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await alt_price_service.update(id=id, data=data, session=session)


@alt_price.delete('/{id}')
async def delete_alt_price(id: int, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await alt_price_service.delete(id=id, session=session)

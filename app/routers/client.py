from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.domain_types import LimitedIntID
from app.services.client_service import client_service

client: APIRouter = APIRouter(prefix='/client', tags=['Client'])


@client.get('/', response_model=list[ClientRead])
async def get_page(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.get_page(session=session)


@client.get('/{id}', response_model=ClientRead)
async def get(session: Annotated[AsyncSession, Depends(db_connect)], id: LimitedIntID):
    return await client_service.get(id=id, session=session)


@client.post('/', response_model=ClientRead)
async def create(data: ClientCreate, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.create(data=data, session=session)


@client.patch('/{id}', response_model=ClientRead)
async def update(
    id: LimitedIntID, data: ClientUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await client_service.update(id=id, data=data, session=session)


@client.delete('/{id}')
async def delete(id: LimitedIntID, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.delete(id=id, session=session)

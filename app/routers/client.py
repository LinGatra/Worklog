from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_connect
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.services.client import client_service

client: APIRouter = APIRouter(prefix='/client')


@client.get('/', response_model=list[ClientRead])
async def get_all_clients(session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.get_all(session=session)


@client.get('/{id}', response_model=ClientRead)
async def get_client_by_id(session: Annotated[AsyncSession, Depends(db_connect)], id: int):
    return await client_service.get_by_id(id=id, session=session)


@client.post('/', response_model=ClientRead)
async def create_client(data: ClientCreate, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.create(data=data, session=session)


@client.patch('/{id}', response_model=ClientRead)
async def update_client(
    id: int, data: ClientUpdate, session: Annotated[AsyncSession, Depends(db_connect)]
):
    return await client_service.update(id=id, data=data, session=session)


@client.delete('/{id}')
async def delete_client(id: int, session: Annotated[AsyncSession, Depends(db_connect)]):
    return await client_service.delete(id=id, session=session)

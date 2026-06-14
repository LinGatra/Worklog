from app.db.base_repository import BaseRepository
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.base_service import BaseService


class ClientService(BaseService[Client, ClientCreate, ClientUpdate]):
    pass


client_repository = BaseRepository(Client)
client_service = ClientService(repo=client_repository)

from app.db.repositories.delete_strategy import SoftDelete
from app.db.repositories.mixins import (
    CreateMixin,
    DeleteMixin,
    DeletionAwareReadMixin,
    DeletionAwareUpdateMixin,
)
from app.models.client import Client
from app.schemas.client import ClientCreateDB, ClientUpdateDB


class ClientRepository(
    CreateMixin[Client, ClientCreateDB],
    DeletionAwareReadMixin[Client],
    DeletionAwareUpdateMixin[Client, ClientUpdateDB],
    DeleteMixin[Client],
):
    model = Client
    deletion = SoftDelete()


client_repository = ClientRepository()

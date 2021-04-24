from datetime import datetime

from pydantic import BaseModel
from ..users.schemas import Employee


class ClientBase(BaseModel):
    name: str
    date_block: datetime


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    is_active: bool
    date_create: datetime
    owner: Employee


class ClientShort(ClientBase):
    id: int
    owner_id: str
    date_create: datetime

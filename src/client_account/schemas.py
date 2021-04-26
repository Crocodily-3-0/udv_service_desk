from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from ..reference_book.schemas import LicenceDB
from ..users.schemas import UserDB


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    is_active: bool = True  # TODO убрать, когда починю default
    owner_id: str


class ClientUpdate(BaseModel):
    # avatar
    pass


class Client(ClientBase):
    id: int
    is_active: bool
    date_create: datetime
    date_block: Optional[datetime]
    owner: UserDB
    employees: List[UserDB]
    licences: List[LicenceDB]


class ClientDB(ClientBase):
    id: int
    is_active: bool
    date_create: datetime
    date_block: Optional[datetime]
    owner_id: str

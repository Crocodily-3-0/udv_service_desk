from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from pydantic.types import UUID4

from ...reference_book.schemas import LicenceDB, SoftwareDB
from ...users.schemas import UserDB


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientCreate):  # TODO доработать изменение заказчика
    owner_id: Optional[UUID4]
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
    software: List[SoftwareDB]


class ClientDB(ClientBase):
    id: int
    is_active: bool
    date_create: datetime
    date_block: Optional[datetime]
    owner_id: UUID4

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator
from pydantic.types import UUID4

from ...reference_book.schemas import LicenceDB, SoftwareDB
from ...users.schemas import UserDB, generate_pwd


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    name: Optional[str]
    owner_id: Optional[str]


class ClientAndOwnerCreate(ClientCreate):
    owner_name: str
    surname: str
    patronymic: Optional[str]
    email: EmailStr
    password: str = generate_pwd()
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class ClientUpdate(ClientBase):  # TODO доработать изменение заказчика
    name: Optional[str]
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
    owner_id: str

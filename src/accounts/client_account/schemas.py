from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator

from ...reference_book.schemas import LicenceDB, SoftwareDB, Licence
from ...users.schemas import UserDB, generate_pwd, Employee, EmployeeList


class ClientBase(BaseModel):
    name: str
    avatar: str


class ClientCreate(ClientBase):
    name: Optional[str]
    owner_id: Optional[str]


class ClientAndOwnerCreate(ClientCreate):
    owner_name: str
    surname: str
    patronymic: Optional[str]
    email: EmailStr
    password: str = generate_pwd()
    avatar: Optional[str]
    owner_avatar: Optional[str]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    owner_licence: int
    licences_list: List[int]

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class ClientUpdate(ClientBase):  # TODO доработать изменение заказчика
    name: Optional[str]
    owner_id: Optional[str]
    avatar: Optional[str]


class ClientDB(ClientBase):
    id: int
    is_active: bool
    avatar: str
    date_create: datetime
    date_block: Optional[datetime]
    owner_id: str


class ClientShort(ClientDB):
    is_active: bool
    owner: UserDB
    count_employees: int = 0


class Client(ClientBase):
    id: int
    is_active: bool
    date_create: datetime
    owner: Employee
    licences: List[Licence]


class ClientPage(BaseModel):
    client: Client
    employees_list: List[EmployeeList]
    licences_list: List[Licence]


class DevClientPage(BaseModel):
    client: Client
    employees_list: List[EmployeeList] = []
    software_list: List[SoftwareDB]


class ClientsPage(BaseModel):
    clients_list: List[ClientShort]
    licences_list: List[LicenceDB]


class EmployeePage(BaseModel):
    employee: Employee
    client: Client
    licences: List[Licence]


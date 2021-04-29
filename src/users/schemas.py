from datetime import datetime

from fastapi_users import models
from pydantic import validator
from typing import Optional


class User(models.BaseUser):
    name: str
    surname: str
    patronymic: Optional[str]
    # is_owner: bool
    # client_id: int
    # date_block: Optional[datetime]


class UserCreate(models.BaseUserCreate):
    name: str
    surname: str
    patronymic: Optional[str]
    # is_owner: bool = False
    # client_id: int
    # date_reg: datetime  # TODO попробовать удалить данное поле из регистрации. Пока без нее не работет
    # date_block: Optional[datetime]

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class EmployeeCreate(UserCreate, models.BaseUserCreate):
    # avatar
    is_owner: bool = False
    client_id: int
    date_reg: datetime


class DeveloperCreate(UserCreate, models.BaseUserCreate):
    # avatar
    date_reg: datetime


class OwnerCreate(UserCreate, models.BaseUserCreate):
    # avatar
    is_owner: bool = True
    client_id: int
    date_reg: datetime


class UserUpdate(User, models.BaseUserUpdate):
    name: Optional[str]
    surname: Optional[str]
    is_owner: Optional[bool]
    is_active: Optional[bool]
    date_block: Optional[datetime]


class UserDB(User, models.BaseUserDB):
    is_active: bool
    is_owner: Optional[bool]
    client_id: Optional[int]
    date_reg: datetime
    date_block: Optional[datetime]

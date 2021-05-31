from datetime import datetime
import random

from fastapi_users import models
from pydantic import validator, EmailStr
from typing import Optional

from src.reference_book.schemas import LicenceDB


def generate_pwd():
    symbols_list = "+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    password = ""
    length = random.randint(6, 10)
    for i in range(length):
        password += random.choice(symbols_list)
    return password


class User(models.BaseUser):
    name: str
    surname: str
    patronymic: Optional[str]
    avatar: Optional[str]
    # is_owner: bool
    # client_id: int
    # date_block: Optional[datetime]


class UserCreate(models.BaseUserCreate):
    name: str
    surname: str
    patronymic: Optional[str]
    avatar: Optional[str]
    password: str = generate_pwd()
    is_owner: Optional[bool] = False
    client_id: Optional[int] = 0
    date_reg: datetime = datetime.utcnow()
    date_block: Optional[datetime]

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class EmployeeCreate(UserCreate, models.BaseUserCreate):
    is_owner: bool = False
    client_id: int
    date_reg: datetime = datetime.utcnow()


class PreEmployeeCreate(EmployeeCreate, models.BaseUserCreate):
    licence_id: int
    client_id: Optional[int]


class DeveloperCreate(UserCreate, models.BaseUserCreate):
    is_superuser = True
    date_reg: datetime = datetime.utcnow()


class OwnerCreate(UserCreate, models.BaseUserCreate):
    is_owner: bool = True
    client_id: int
    date_reg: datetime = datetime.utcnow()


class UserUpdate(User, models.BaseUserUpdate):
    name: Optional[str]
    surname: Optional[str]
    is_owner: Optional[bool] = False
    is_active: Optional[bool]
    date_block: Optional[datetime]
    email: Optional[EmailStr]


class UserDB(User, models.BaseUserDB):
    is_active: bool = True  # TODO проверить зачем здесь был " = True"
    is_owner: Optional[bool]
    client_id: Optional[int]
    date_reg: datetime = datetime.utcnow()  # TODO проверить можно ли убрать " = datetime.utcnow()"
    date_block: Optional[datetime]


class Employee(UserDB):
    licence: Optional[LicenceDB]


class EmployeeUpdate(UserUpdate):
    licence_id: Optional[int]


class EmployeeList(Employee):
    count_appeals: int


class DeveloperList(User):
    count_appeals: int

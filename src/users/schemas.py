from datetime import datetime

from fastapi_users import models
from pydantic import validator
from typing import Optional


class Employee(models.BaseUser):
    name: str
    surname: str
    patronymic: Optional[str]
    is_owner: bool
    client: int
    date_block: Optional[datetime]


class EmployeeCreate(models.BaseUserCreate):
    name: str
    surname: str
    patronymic: Optional[str]
    is_owner: bool = False
    client: int
    date_reg: datetime  # TODO попробовать удалить данное поле из регистрации. Пока без нее не работет
    date_block: Optional[datetime]

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class EmployeeUpdate(Employee, models.BaseUserUpdate):
    pass


class EmployeeDB(Employee, models.BaseUserDB):
    date_reg: datetime


class Developer(models.BaseUser):
    name: str
    surname: str
    patronymic: Optional[str]
    is_superuser: Optional[bool] = True


class DeveloperCreate(models.BaseUserCreate):
    name: str
    surname: str
    patronymic: Optional[str]

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class DeveloperUpdate(Developer, models.BaseUserUpdate):
    pass


class DeveloperDB(Developer, models.BaseUserDB):
    pass

from datetime import datetime

from fastapi_users import models
from pydantic import validator
from typing import Optional


class User(models.BaseUser):
    name: str
    surname: str
    patronymic: Optional[str]
    is_owner: bool
    client: int
    date_block: Optional[datetime]


class UserCreate(models.BaseUserCreate):
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


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    date_reg: datetime

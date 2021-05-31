from typing import Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.db.db import database
from src.service import send_mail
from src.users.logic import all_users, delete_user, pre_update_user
from src.users.models import users
from src.users.schemas import UserCreate, DeveloperCreate, UserUpdate, UserDB


async def get_developer(developer_id: str) -> Optional[UserDB]:
    query = users.select().where((users.c.is_superuser == 1) & (users.c.id == developer_id))
    developer = await database.fetch_one(query=query)
    if developer:
        return UserDB(**dict(developer))
    return None


async def add_developer(developer: DeveloperCreate) -> UserDB:
    developer = DeveloperCreate(**dict({**dict(developer), "is_superuser": True}))
    try:
        created_developer = await all_users.create_user(developer, safe=False)
    except Exception:
        print(Exception)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    message = f"Добро пожаловать в UDV Service Desk!\n\nВаш логин в системе: " \
              f"{developer.email}\nВаш пароль: {developer.password}"
    await send_mail(developer.email, "Вы зарегистрированы в системе", message)
    return created_developer


async def delete_developer(id: UUID4):
    await delete_user(id)

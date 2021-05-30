from typing import Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.db.db import database
from src.service import send_mail
from src.users.logic import all_users, delete_user, pre_update_user
from src.users.models import users
from src.users.schemas import UserCreate, DeveloperCreate, UserUpdate, UserDB


async def get_developer(id: UUID4) -> Optional[UserDB]:
    query = users.select().where((users.c.is_superuser is True) & (users.c.id == id))
    developer = await database.fetch_one(query=query)
    if developer:
        return UserDB(**dict(developer))
    return None


async def add_developer(user: UserCreate) -> UserDB:
    developer = DeveloperCreate(**user.dict())
    try:
        created_developer = await all_users.create_user(developer, safe=False)
    except Exception:
        print(Exception)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    message = f"Добро пожаловать в UDV Service Desk!\n\nВаш логин в системе: {user.email}\nВаш пароль: {user.password}"
    await send_mail(user.email, "Вы зарегистрированы в системе", message)
    return created_developer


async def delete_developer(id: UUID4):
    await delete_user(id)

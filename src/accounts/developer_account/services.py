from typing import Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.db.db import database
from src.service import send_mail, Email
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
    await send_mail_with_dev_pwd(developer)
    return created_developer


async def send_mail_with_dev_pwd(user: DeveloperCreate) -> None:
    message = f"Добро пожаловать в UDV Service Desk!\n\n" \
              f"Ваш логин в системе: {user.email}\nВаш пароль: {user.password}"
    email = Email(recipient=user.email, title="Регистрация в UDV Service Desk", message=message)
    await send_mail(email)


async def delete_developer(id: UUID4):
    await delete_user(id)

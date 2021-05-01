from datetime import datetime

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.db.db import database
from src.users.logic import all_users, delete_user, update_user
from src.users.models import users
from src.users.schemas import UserCreate, DeveloperCreate, UserUpdate


async def get_developer(id: UUID4):
    developer = await database.fetch_one(users.select().where((users.c.is_superuser is True) & (users.c.id == id)))
    if developer:
        developer = dict(developer)
        return developer
    return None


async def add_developer(user: UserCreate):
    developer = DeveloperCreate(
        **user.dict(),
        date_reg=datetime.utcnow())
    try:
        created_developer = await all_users.create_user(developer, safe=True)
    except Exception:
        print(Exception)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )

    return created_developer


async def update_developer(id: UUID4, item: UserUpdate):
    update_dict = item.dict(exclude_unset=True)
    updated_developer = await update_user(id, update_dict)
    return updated_developer


async def delete_developer(id: UUID4):
    await delete_user(id)

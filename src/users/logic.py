from fastapi import HTTPException, Depends, status, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.password import get_password_hash

from ..config import SECRET
from .schemas import User, UserCreate, UserUpdate, UserDB
from .models import user_db, UserTable, users
from src.db.db import database
from src.errors import Errors

from typing import Dict, Any
from pydantic.types import UUID4
# from requests import Request


auth_backends = []

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)

auth_backends.append(jwt_authentication)

all_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

any_user = all_users.current_user(active=True)
employee = all_users.current_user(active=True, superuser=False)
developer_user = all_users.current_user(active=True, superuser=True)


async def get_owner(client_id: int, user: UserTable = Depends(any_user)):
    if not (user.client_id == client_id and user.is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_owner_with_superuser(client_id: int, user: UserTable = Depends(any_user)):
    if not user.is_superuser and not (user.client_id == client_id and user.is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_client_users(client_id: int, user: UserTable = Depends(any_user)):
    if user.client_id != client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_client_users_with_superuser(client_id: int, user: UserTable = Depends(any_user)):
    if not user.is_superuser and user.client_id != client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


async def on_after_reset_password(user: UserDB, request: Request):
    print(f"User {user.id} has reset their password.")


async def after_verification_request(user: UserDB, token: str, request: Request):
    print(f"Verification requested for user {user.id}. Verification token: {token}")


async def after_verification(user: UserDB, request: Request):
    print(f"{user.id} is now verified.")


async def get_or_404(id: UUID4) -> UserDB:
    user = await database.fetch_one(query=users.select().where(users.c.id == id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND)
    return user


async def update_user(id: UUID4, update_dict: Dict[str, Any]):
    user = await get_or_404(id)
    user = {**user}
    for field in update_dict:
        if field == "password":
            hashed_password = get_password_hash(update_dict[field])
            user["hashed_password"] = hashed_password
        else:
            user[field] = update_dict[field]

    updated_user = await user_db.update(UserDB(**user))

    return updated_user


async def delete_user(id: UUID4):
    user = await get_or_404(id)
    await user_db.delete(user)
    return None

from fastapi import HTTPException, Depends, status
from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from requests import Request

from ..config import SECRET
from .schemas import User, UserCreate, UserUpdate, UserDB
from .models import user_db, UserTable

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


async def get_owner(user: UserTable = Depends(any_user)):
    if not user.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_owner_with_superuser(user: UserTable = Depends(any_user)):
    if not user.is_superuser and not user.is_owner:
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

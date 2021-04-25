from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from requests import Request

from ..config import SECRET
from .schemas import User, UserCreate, UserUpdate, UserDB
from .models import user_db

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


async def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


async def on_after_reset_password(user: UserDB, request: Request):
    print(f"User {user.id} has reset their password.")


async def after_verification_request(user: UserDB, token: str, request: Request):
    print(f"Verification requested for user {user.id}. Verification token: {token}")


async def after_verification(user: UserDB, request: Request):
    print(f"{user.id} is now verified.")

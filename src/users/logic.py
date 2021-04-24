from typing import Union

from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from requests import Request

from ..config import SECRET
from .schemas import Employee, EmployeeCreate, EmployeeUpdate, EmployeeDB, \
    Developer, DeveloperCreate, DeveloperUpdate, DeveloperDB
from .models import employee_db, developer_db

auth_backends = []

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)

auth_backends.append(jwt_authentication)


employee_users = FastAPIUsers(
    employee_db,
    auth_backends,
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeDB,
)


developer_users = FastAPIUsers(
    developer_db,
    auth_backends,
    Developer,
    DeveloperCreate,
    DeveloperUpdate,
    DeveloperDB,
)


async def on_after_forgot_password(user: Union[EmployeeDB, DeveloperDB], token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


async def on_after_reset_password(user: Union[EmployeeDB, DeveloperDB], request: Request):
    print(f"User {user.id} has reset their password.")


async def after_verification_request(user: Union[EmployeeDB, DeveloperDB], token: str, request: Request):
    print(f"Verification requested for user {user.id}. Verification token: {token}")


async def after_verification(user: Union[EmployeeDB, DeveloperDB], request: Request):
    print(f"{user.id} is now verified.")

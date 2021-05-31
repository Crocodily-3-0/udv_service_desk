from datetime import datetime

from fastapi import HTTPException, Depends, status, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.password import get_password_hash
from fastapi_users.router import ErrorCode

from ..config import SECRET
from .schemas import User, UserCreate, UserUpdate, UserDB, DeveloperList, generate_pwd, EmployeeUpdate, DeveloperCreate
from .models import user_db, UserTable, users
from src.db.db import database
from src.errors import Errors

from typing import Dict, Any, List, Optional
from pydantic.types import UUID4
from pydantic import EmailStr
from ..desk.models import appeals
from ..reference_book.services import update_employee_licence
from ..service import send_mail

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


async def get_count_dev_appeals(developer_id: str) -> int:
    query = appeals.select().where(appeals.c.responsible_id == developer_id)
    result = await database.fetch_all(query=query)
    return len(result)  # TODO проверить не будет ли ошибки на len(None)


async def get_developers() -> List[DeveloperList]:
    query = users.select().where(users.c.is_superuser == 1)
    result = await database.fetch_all(query=query)
    developers = []
    for developer in result:
        developer = dict(developer)
        print(developer)
        count_appeals = await get_count_dev_appeals(str(developer["id"]))
        developers.append(DeveloperList(**dict({**developer, "count_appeals": count_appeals})))
    return developers


async def get_or_404(id: UUID4) -> UserDB:
    user = await database.fetch_one(query=users.select().where(users.c.id == id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND)
    return user


async def get_user(id: UUID4) -> Optional[UserDB]:
    user = await database.fetch_one(query=users.select().where(users.c.id == id))
    return user


async def pre_update_user(id: UUID4, item: EmployeeUpdate) -> UserDB:
    if item.licence_id:
        licence = await update_employee_licence(id, item.licence_id)
    update_employee = UserUpdate(**dict(item))
    update_dict = update_employee.dict(exclude_unset=True)
    updated_user = await update_user(id, update_dict)
    return updated_user


async def pre_update_developer(id: UUID4, item: UserUpdate) -> UserDB:
    update_dict = item.dict(exclude_unset=True)
    if "email" in update_dict.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.FORBIDDEN_CHANGE_EMAIL
        )
    updated_developer = await update_user(id, update_dict)
    return updated_developer


async def update_user(id: UUID4, update_dict: Dict[str, Any]) -> UserDB:
    user = await get_or_404(id)
    user = dict(user)
    for field in update_dict:
        if field == "password":
            hashed_password = get_password_hash(update_dict[field])
            user["hashed_password"] = hashed_password
        elif update_dict[field]:
            user[field] = update_dict[field]

    updated_user = await user_db.update(UserDB(**user))

    return updated_user


async def delete_user(id: UUID4):
    user = await get_or_404(id)
    await user_db.delete(user)
    return None


async def create_developer():
    developer = DeveloperCreate(
        email="admin@py.com",
        password="123456",
        is_active=True,
        is_superuser=True,
        is_verified=False,
        name="admin",
        surname="string",
        patronymic="string",
        avatar="string",
        is_owner=False,
        client_id=0,
        date_reg=datetime.utcnow(),
    )
    try:
        created_developer = await all_users.create_user(developer, safe=False)
    except Exception:
        print(Exception)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    return created_developer


async def get_user_by_email(email: EmailStr) -> UserDB:
    user = await database.fetch_one(query=users.select().where(users.c.email == email))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND)
    return user


async def change_pwd(id: UUID4, pwd: str) -> UserDB:
    if len(pwd) < 6:
        raise ValueError('Password should be at least 6 characters')
    updated_user = EmployeeUpdate(**dict({"password": pwd}))
    updated_user = await pre_update_user(id, updated_user)

    message = f"Добрый день!\nВы изменили свой пароль на: {pwd}\n" \
              f"Если Вы не меняли пароль обратитесь к администратору или смените его самостоятельно"
    await send_mail(updated_user.email, "Вы зарегистрированы в системе", message)
    return updated_user


async def get_new_password(email: EmailStr) -> UserDB:
    user = await get_user_by_email(email)
    pwd = await generate_pwd()

    message = f"Добрый день!\nВаш новый пароль: {pwd}\n" \
              f"Если Вы не меняли пароль обратитесь к администратору или смените его самостоятельно"
    await send_mail(user.email, "Вы зарегистрированы в системе", message)

    return await change_pwd(user.id, pwd)

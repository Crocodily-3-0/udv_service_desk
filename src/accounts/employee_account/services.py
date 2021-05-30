from typing import Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.accounts.client_account.schemas import EmployeePage
from src.accounts.client_account.services import get_client, get_employees
from src.db.db import database
from src.reference_book.services import get_client_licences, add_employee_licence
from src.service import send_mail
from src.users.logic import all_users, update_user, delete_user
from src.users.models import users
from src.users.schemas import EmployeeCreate, PreEmployeeCreate, UserDB


async def get_employee(client_id: int, pk: UUID4) -> Optional[EmployeePage]:
    employee = await database.fetch_one(users.select().where((users.c.client_id == client_id) & (users.c.id == pk)))
    if employee:
        employee = dict(employee)
        client = await get_client(client_id)
        client_licences = client.licences
        return EmployeePage(**dict({**employee, "client": client, "licences": client_licences}))
    return None


async def get_count_allowed_employees(client_id: int) -> int:
    count_allowed_employees = 0
    client_licences = await get_client_licences(client_id)
    for licence in client_licences:
        count_allowed_employees += licence.count_members
    client_employees = await get_employees(client_id)
    return count_allowed_employees - len(client_employees)


async def add_employee(id: int, user: PreEmployeeCreate) -> UserDB:
    user.client_id = id
    user.is_owner = False
    employee = EmployeeCreate(**user.dict())
    try:
        created_user = await all_users.create_user(employee, safe=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    licence_id = user.licence_id
    licence = await add_employee_licence(created_user.id, licence_id)

    message = f"Добро пожаловать в UDV Service Desk!\n\nВаш логин в системе: {user.email}\nВаш пароль: {user.password}"
    await send_mail(user.email, "Вы зарегистрированы в системе", message)
    return created_user


async def delete_employee(pk: UUID4):
    await delete_user(pk)


async def block_employee(pk: UUID4):
    update_dict = {"is_active": False}
    updated_employee = await update_user(pk, update_dict)
    return updated_employee

from datetime import datetime

from fastapi import HTTPException, status, Request
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from src.db.db import database
from src.reference_book.models import licences
from src.users.logic import all_users, update_user, delete_user
from src.users.models import users
from src.users.schemas import UserCreate, EmployeeCreate, UserUpdate


async def get_employees(id: int):
    employees_data = await database.fetch_all(users.select().where(users.c.client_id == id))
    result = [dict(employee) for employee in employees_data]
    return result


async def get_employee(id: int, pk: str):
    employee = await database.fetch_one(users.select().where((users.c.client_id == id) & (users.c.id == pk)))
    if employee:
        employee = dict(employee)
        return employee
    return None


async def count_allowed_employees(client_id: int):
    count = 0
    licence_data = await database.fetch_all(query=licences.select().where(licences.c.client_id == client_id))
    licences_dict = [dict(licence) for licence in licence_data]
    for licence in licences_dict:
        count += licence["count_members"]

    query = users.select().where((users.c.client_id == client_id) & (users.c.is_active is True))
    employee_data = await database.fetch_all(query=query)
    employee_dict = [dict(employee) for employee in employee_data]
    return count - len(employee_dict)


async def add_employee(id: int, user: UserCreate):
    employee = EmployeeCreate(
        **user.dict(),
        client_id=id,
        is_owner=False,
        date_reg=datetime.utcnow())
    try:
        created_user = await all_users.create_user(employee, safe=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )

    return created_user


async def update_employee(pk: UUID4, item: UserUpdate):
    update_dict = item.dict(exclude_unset=True)
    updated_employee = await update_user(pk, update_dict)
    return updated_employee


async def delete_employee(pk: UUID4):
    await delete_user(pk)


async def block_employee(pk: UUID4):
    update_dict = {"is_active": False}
    updated_employee = await update_user(pk, update_dict)
    return updated_employee

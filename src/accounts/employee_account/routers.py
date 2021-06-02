from typing import Optional

from fastapi import APIRouter, status, Depends, HTTPException, Response
from pydantic.types import UUID4

from .services import add_employee, get_count_allowed_employees, get_employee, delete_employee, block_employee
from src.errors import Errors
from src.users.logic import get_owner, any_user, get_client_users_with_superuser, pre_update_user, change_pwd, \
    get_email_with_changed_pwd
from src.users.models import UserTable
from src.users.schemas import UserDB, PreEmployeeCreate, EmployeeUpdate
from ..client_account.schemas import EmployeePage
from ..client_account.services import update_client_owner

employee_router = APIRouter()


@employee_router.get("/{id}/employees/{pk}", response_model=Optional[EmployeePage], status_code=status.HTTP_200_OK)
async def employee(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_employee(id, pk)


@employee_router.post("/{id}/employees", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def create_employee(id: int, item: PreEmployeeCreate, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    if await get_count_allowed_employees(id) > 0:
        return await add_employee(id, item)
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Errors.CLIENT_HAS_NOT_FREE_VACANCIES,
        )


@employee_router.patch("/{id}/employees/{pk}", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def update_employee_by_id(id: int, pk: UUID4, item: EmployeeUpdate, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    return await pre_update_user(pk, item)


@employee_router.patch("/{id}/employees/{pk}/make_owner", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def make_employee_owner(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    return await update_client_owner(id, pk)


@employee_router.patch("/{id}/employees/{pk}/block", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def block_employee_by_id(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    return await block_employee(pk)


@employee_router.patch("/{id}/employees/{pk}/pwd", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def change_employee_pwd(id: int, pk: UUID4, new_pwd: str, user: UserTable = Depends(any_user)):
    if str(user.id) == str(pk):
        email = await get_email_with_changed_pwd(new_pwd, user)
        return await change_pwd(pk, new_pwd, email)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@employee_router.delete("/{id}/employees/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_by_id(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    if user.id == pk:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Errors.IMPOSSIBLE_DELETE_OWNER,
        )

    await delete_employee(pk)

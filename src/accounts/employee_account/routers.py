from typing import List

from fastapi import APIRouter, Request, status, Depends, HTTPException, Response
from pydantic.types import UUID4

from .services import add_employee, count_allowed_employees, get_employees, \
    get_employee, update_employee, delete_employee, block_employee
from src.errors import Errors
from src.users.logic import get_owner, any_user, get_client_users_with_superuser
from src.users.models import UserTable
from src.users.schemas import UserCreate, UserDB, UserUpdate

employee_router = APIRouter()


@employee_router.get("/{id}/employees", response_model=List[UserDB], status_code=status.HTTP_200_OK)
async def employees_list(id: int, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_employees(id)


@employee_router.get("/{id}/employees/{pk}", response_model=UserDB, status_code=status.HTTP_200_OK)
async def employee(id: int, pk: str, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_employee(id, pk)


@employee_router.post("/{id}/employees", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def create_employee(id: int, item: UserCreate, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    if await count_allowed_employees(id):
        return await add_employee(id, item)
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Errors.NO_VACANCIES_UNDER_LICENCES,
        )


@employee_router.patch("/{id}/employees/{pk}", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def update_employee_by_id(id: int, pk: UUID4, item: UserUpdate, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    return await update_employee(pk, item)


@employee_router.patch("/{id}/employees/{pk}/block", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def block_employee_by_id(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    return await block_employee(pk)


@employee_router.delete("/{id}/employees/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_by_id(id: int, pk: UUID4, user: UserTable = Depends(any_user)):
    user = await get_owner(id, user)
    if user.id == pk:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Errors.IMPOSSIBLE_DELETE_OWNER,
        )

    await delete_employee(pk)

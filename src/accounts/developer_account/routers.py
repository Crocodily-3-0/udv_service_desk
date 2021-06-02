from typing import List

from fastapi import APIRouter, Depends, status, Response, HTTPException
from pydantic.types import UUID4

from .services import get_developer, add_developer, delete_developer
from src.users.models import UserTable
from src.users.logic import developer_user, get_developers, change_pwd, pre_update_developer, \
    get_email_with_changed_pwd, default_uuid
from src.users.schemas import UserDB, UserUpdate, DeveloperList, DeveloperCreate
from .statistics.routers import statistics_router


developer_router = APIRouter()


@developer_router.get("/", response_model=List[DeveloperList], status_code=status.HTTP_200_OK)
async def developers_list(user: UserTable = Depends(developer_user), last_id: UUID4 = default_uuid, limit: int = 9):
    return await get_developers(last_id, limit)


@developer_router.get("/{id:uuid}", response_model=UserDB, status_code=status.HTTP_200_OK)
async def developer(id: UUID4, user: UserTable = Depends(developer_user)):
    return await get_developer(str(id))


@developer_router.post("/")
async def create_developer(item: DeveloperCreate, user: UserTable = Depends(developer_user)):
    return await add_developer(item)


@developer_router.patch("/{id:uuid}", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def update_developer_by_id(id: UUID4, item: UserUpdate, user: UserTable = Depends(developer_user)):
    return await pre_update_developer(id, item)


@developer_router.patch("/{id:uuid}/pwd", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def change_dev_pwd(id: UUID4, new_pwd: str, user: UserTable = Depends(developer_user)):
    if str(user.id) == str(id):
        email = await get_email_with_changed_pwd(new_pwd, user)
        return await change_pwd(id, new_pwd, email)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@developer_router.delete("/{id:uuid}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_developer_by_id(id: UUID4, user: UserTable = Depends(developer_user)):
    await delete_developer(id)


developer_router.include_router(statistics_router, prefix='/statistics', tags=['Statistics'])

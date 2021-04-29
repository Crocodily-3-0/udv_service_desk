from typing import List

from fastapi import APIRouter, Depends, status, Response
from pydantic.types import UUID4

from .services import get_developer, add_developer, update_developer, delete_developer
from src.users.models import UserTable
from src.users.logic import developer_user, get_developers
from src.users.schemas import UserDB, UserCreate, UserUpdate

developer_router = APIRouter()


@developer_router.get("/", response_model=List[UserDB], status_code=status.HTTP_200_OK)
async def developers_list(user: UserTable = Depends(developer_user)):
    return await get_developers()


@developer_router.get("/{id:uuid}", response_model=UserDB, status_code=status.HTTP_200_OK)
async def developer(id: UUID4, user: UserTable = Depends(developer_user)):
    return await get_developer(id)


@developer_router.post("/")
async def create_developer(item: UserCreate, user: UserTable = Depends(developer_user)):
    return await add_developer(item)


@developer_router.patch("/{id:uuid}", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def update_developer_by_id(id: UUID4, item: UserUpdate, user: UserTable = Depends(developer_user)):
    return await update_developer(id, item)


@developer_router.delete("/{id:uuid}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_developer_by_id(id: UUID4, user: UserTable = Depends(developer_user)):
    await delete_developer(id)

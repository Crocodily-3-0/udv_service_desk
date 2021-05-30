from typing import List, Union

from fastapi import APIRouter, Depends, status, Request, HTTPException
from .schemas import ClientDB, Client, ClientCreate, ClientUpdate, ClientAndOwnerCreate, ClientsPage, ClientPage, \
    DevClientPage
from .services import get_clients, get_client, add_client, update_client, add_owner, get_client_owner, update_client_owner, \
    get_clients_page, get_client_page, block_client, get_dev_client_page, get_client_info
from src.users.models import UserTable
from src.users.logic import developer_user, any_user, get_client_users_with_superuser, get_owner_with_superuser, \
    get_client_users
from ..employee_account.routers import employee_router
from ...users.schemas import UserCreate

client_router = APIRouter()


@client_router.get("/", response_model=ClientsPage, status_code=status.HTTP_200_OK)
async def clients_list(user: UserTable = Depends(developer_user)):
    return await get_clients_page()


@client_router.post("/", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def create_client(item: ClientAndOwnerCreate, user: UserTable = Depends(developer_user)):
    new_client = await add_client(item)
    return new_client


@client_router.get("/{id}", response_model=Union[ClientPage, DevClientPage], status_code=status.HTTP_200_OK)
async def client(id: int, user: UserTable = Depends(any_user)):
    if user.is_superuser:
        return await get_dev_client_page(id)
    elif await get_client_users(id, user):
        return await get_client_page(id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@client_router.get("/{id}/info", response_model=Client, status_code=status.HTTP_200_OK)
async def client_info(id: int, user: UserTable = Depends(any_user)):
    user = await get_owner_with_superuser(id, user)
    return await get_client_info(id)


@client_router.patch("/{id}/info", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def update_client_by_id(id: int, item: ClientUpdate, user: UserTable = Depends(any_user)):
    # TODO разделить изменение аватарки владельцем и изменение владельца владельцем или разработчиком
    user = await get_owner_with_superuser(id, user)
    return await update_client(id, item)


@client_router.patch("/{id}/block", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def block_client_by_id(id: int, user: UserTable = Depends(developer_user)):
    return await block_client(id)


client_router.include_router(employee_router)

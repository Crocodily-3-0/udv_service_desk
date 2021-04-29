from typing import List

from fastapi import APIRouter, Depends, status, Request
from .schemas import ClientDB, Client, ClientCreate, ClientUpdate
from .services import get_clients, get_client, add_client, update_client, add_owner, get_client_owner, update_owner
from src.users.models import UserTable
from src.users.logic import developer_user, any_user, get_client_users_with_superuser, get_owner_with_superuser
from src.reference_book.api.licence import client_licences_router
from ..employee_account.routers import employee_router
from ...users.schemas import UserCreate

client_router = APIRouter()


@client_router.get("/", response_model=List[ClientDB], status_code=status.HTTP_200_OK)
async def clients_list(user: UserTable = Depends(developer_user)):
    return await get_clients()


@client_router.post("/", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def create_client(item: ClientCreate, user: UserTable = Depends(developer_user)):
    return await add_client(item)


@client_router.get("/{id}", response_model=Client, status_code=status.HTTP_200_OK)
async def client(id: int, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_client(id)


@client_router.put("/{id}", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def update_client_by_id(id: int, item: ClientUpdate, user: UserTable = Depends(any_user)):
    # TODO разделить изменение аватарки владельцем и изменение владельца владельцем или разработчиком
    user = get_owner_with_superuser(id, user)
    return await update_client(id, item)


@client_router.get("/{id}/owner", status_code=status.HTTP_200_OK)
async def owner(id: int, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_client_owner(id)


@client_router.post("/{id}/owner", status_code=status.HTTP_201_CREATED)
async def create_owner(id: int, item: UserCreate, user: UserTable = Depends(developer_user)):
    return await add_owner(id, item)


@client_router.patch("/{id}/owner", status_code=status.HTTP_201_CREATED)
async def change_owner(id: int, item: ClientUpdate, user: UserTable = Depends(developer_user)):
    user = get_owner_with_superuser(id, user)
    return await update_owner(id, item.owner_id)


client_router.include_router(client_licences_router)
client_router.include_router(employee_router)

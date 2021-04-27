from typing import List

from fastapi import APIRouter, Depends, status
from .schemas import ClientDB, Client, ClientCreate, ClientUpdate
from .services import get_clients, get_client, add_client
from ..users.models import UserTable
from ..users.logic import developer_user, any_user, get_client_users_with_superuser, get_owner
from src.reference_book.api.licence import for_client_router

router = APIRouter()


@router.get("/", response_model=List[ClientDB], status_code=status.HTTP_200_OK)
async def clients_list(user: UserTable = Depends(developer_user)):
    return await get_clients()


@router.post("/", response_model=ClientDB, status_code=status.HTTP_201_CREATED)
async def create_client(item: ClientCreate, user: UserTable = Depends(developer_user)):
    return await add_client(item)


@router.get("/{id}", response_model=Client, status_code=status.HTTP_200_OK)
async def client(id: int, user: UserTable = Depends(any_user)):
    user = await get_client_users_with_superuser(id, user)
    return await get_client(id)


# @router.put("/{id}", response_model=Client, status_code=status.HTTP_201_CREATED)
# async def client(id: int, item: ClientUpdate, user: UserTable = Depends(get_owner)):
#     user = get_client_users_with_superuser(id, user)
#     return await update_client(id, item)


router.include_router(for_client_router)

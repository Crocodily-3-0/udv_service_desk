from typing import List

from fastapi import APIRouter
from .schemas import ClientShort, Client
from .services import get_clients, get_client

router = APIRouter()


@router.get("/", response_model=List[ClientShort])
async def clients_list():
    return await get_clients()


@router.get("/{id}", response_model=Client)
async def client(id: int):
    return await get_client(id)

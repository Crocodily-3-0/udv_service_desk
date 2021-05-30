from typing import List

from fastapi import APIRouter, status, Depends, Response
from ..schemas import ModuleCreate, ModuleDB, ModuleUpdate
from ..services import get_module, add_module, delete_module, update_module, get_modules
from ...users.logic import developer_user
from ...users.models import UserTable

router = APIRouter()


@router.get('/', response_model=List[ModuleDB], status_code=status.HTTP_200_OK)
async def modules_list(user: UserTable = Depends(developer_user)):
    return await get_modules()


@router.get('/{id}', response_model=ModuleDB, status_code=status.HTTP_200_OK)
async def module(id: int, user: UserTable = Depends(developer_user)):
    return await get_module(id)


@router.post("/", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def create_module(item: ModuleCreate, user: UserTable = Depends(developer_user)):
    return await add_module(item)


@router.put("/{id}", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def update_module_by_id(id: int, item: ModuleUpdate, user: UserTable = Depends(developer_user)):
    return await update_module(id, item)


@router.delete("/{id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_module_by_id(id: int, user: UserTable = Depends(developer_user)):
    await delete_module(id)

from typing import List

from fastapi import APIRouter, status
from ..schemas import Module, ModuleShort, ModuleCreate, ModuleDB
from ..services import get_module, get_modules, add_module, delete_module, update_module

router = APIRouter()


@router.get("/", response_model=List[ModuleShort], status_code=status.HTTP_200_OK)
async def module_list():
    return await get_modules()


@router.get('/{id}', response_model=Module, status_code=status.HTTP_200_OK)
async def module(id: int):
    return await get_module(id)


@router.post("/", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def create_module(item: ModuleCreate):
    return await add_module(item)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module_by_id(id: int):
    return await delete_module(id)


@router.put("/{id}", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def update_module_by_id(id: int, item: ModuleCreate):
    return await update_module(id, item)

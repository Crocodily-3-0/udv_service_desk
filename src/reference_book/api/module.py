from typing import List

from fastapi import APIRouter
from ..schemas import Module, ModuleShort, ModuleCreate
from ..services import get_module, get_modules, add_module, delete_module, update_module

router = APIRouter()


@router.get("/", response_model=List[ModuleShort])
async def module_list():
    return await get_modules()


@router.get('/{id}', response_model=Module)
async def module(id: int):
    return await get_module(id)


@router.post("/")
async def create_module(item: ModuleCreate):
    return await add_module(item)


@router.delete("/{id}")
async def delete_module(id: int):
    return await delete_module(id)


@router.put("/{id}")
async def update_module(id: int, item: ModuleCreate):
    return await update_module(id, item)

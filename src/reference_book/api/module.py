from fastapi import APIRouter, status, Depends, Response
from ..schemas import Module, ModuleCreate, ModuleDB
from ..services import get_module, add_module, delete_module, update_module
from ...users.logic import developer_user
from ...users.models import UserTable

router = APIRouter()


@router.get('/{id}/modules/{pk}', response_model=Module, status_code=status.HTTP_200_OK)
async def module(id: int, pk: int, user: UserTable = Depends(developer_user)):
    return await get_module(id, pk)


@router.post("/{id}/modules/", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def create_module(id, item: ModuleCreate, user: UserTable = Depends(developer_user)):
    return await add_module(id, item)


@router.put("/{id}/modules/{pk}", response_model=ModuleDB, status_code=status.HTTP_201_CREATED)
async def update_module_by_id(id: int, pk: int, item: ModuleCreate, user: UserTable = Depends(developer_user)):
    return await update_module(id, pk, item)


@router.delete("/{id}/modules/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_module_by_id(id: int, pk: int, user: UserTable = Depends(developer_user)):
    await delete_module(id, pk)

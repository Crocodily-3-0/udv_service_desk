from typing import List

from fastapi import APIRouter, status, Depends, Response

from ..services import get_software, get_softwares, get_software_with_modules, \
    add_software, delete_software, update_software
from ..schemas import Software, SoftwareDB, SoftwareCreate
from ...users.logic import developer_user
from ...users.models import UserTable
from .module import router as module_router

router = APIRouter()


@router.get('/', response_model=List[SoftwareDB], status_code=status.HTTP_200_OK)
async def software_list(user: UserTable = Depends(developer_user)):
    return await get_softwares()


@router.get('/{id}', response_model=SoftwareDB, status_code=status.HTTP_200_OK)
async def software(id: int, user: UserTable = Depends(developer_user)):
    return await get_software(id)


@router.get("/{id}/modules", response_model=Software, status_code=status.HTTP_200_OK)
async def get_software_modules(id: int, user: UserTable = Depends(developer_user)):
    return await get_software_with_modules(id)


@router.post("/", response_model=SoftwareDB, status_code=status.HTTP_201_CREATED)
async def create_software(software: SoftwareCreate, user: UserTable = Depends(developer_user)):
    return await add_software(software)


@router.put("/{id}", response_model=SoftwareDB, status_code=status.HTTP_201_CREATED)
async def update_software_by_id(id: int, item: SoftwareCreate, user: UserTable = Depends(developer_user)):
    return await update_software(id, item)


@router.delete("/{id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_software_by_id(id: int, user: UserTable = Depends(developer_user)):
    await delete_software(id)


router.include_router(module_router)

from typing import List

from fastapi import APIRouter, Depends, status
from .software import router as software_router, software_list
from .licence import router as licence_router, licence_list
from ..schemas import ModuleShort
from ..services import get_modules
from ...users.logic import developer_user
from ...users.models import UserTable

router = APIRouter()


@router.get("/modules", response_model=List[ModuleShort], status_code=status.HTTP_200_OK)
async def module_list(user: UserTable = Depends(developer_user)):
    return await get_modules()


@router.get('/', status_code=status.HTTP_200_OK)
async def get_reference_book(user: UserTable = Depends(developer_user)):
    licences = await licence_list(user)
    modules = await module_list(user)
    softwares = await software_list(user)
    return {"licences": licences, "modules": modules, "softwares": softwares}

router.include_router(licence_router, prefix='/licences')
router.include_router(software_router, prefix='/software')

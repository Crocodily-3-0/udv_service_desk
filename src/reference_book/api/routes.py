from fastapi import APIRouter, Depends, status
from .software import router as software_router, software_list
from .licence import router as licence_router, licence_list
from .module import router as module_router, modules_list
from ...users.logic import developer_user
from ...users.models import UserTable

router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK)
async def get_reference_book(user: UserTable = Depends(developer_user)):  # TODO разобраться с доступом
    licences = await licence_list(user)
    modules = await modules_list(user)
    softwares = await software_list(user)
    return {"licences": licences, "modules": modules, "softwares": softwares}

router.include_router(licence_router, prefix='/licences')
router.include_router(software_router, prefix='/software')
router.include_router(module_router, prefix='/modules')

from fastapi import APIRouter, status, Depends, Response

from ..services import get_software_with_modules, delete_software, update_software, \
    get_software_page, add_software_with_modules
from ..schemas import Software, SoftwareDB, SoftwareUpdate, SoftwarePage, SoftwareWithModulesCreate
from ...users.logic import developer_user
from ...users.models import UserTable

router = APIRouter()


@router.get('/', response_model=SoftwarePage, status_code=status.HTTP_200_OK)
async def software_list(last_id: int = 0, limit: int = 9, user: UserTable = Depends(developer_user)):
    return await get_software_page(last_id, limit)


@router.get('/{id}', response_model=Software, status_code=status.HTTP_200_OK)
async def software(id: int, user: UserTable = Depends(developer_user)):
    return await get_software_with_modules(id)


@router.post("/", response_model=SoftwareDB, status_code=status.HTTP_201_CREATED)
async def create_software(new_software: SoftwareWithModulesCreate, user: UserTable = Depends(developer_user)):
    return await add_software_with_modules(new_software)


@router.patch("/{id}", response_model=SoftwareDB, status_code=status.HTTP_201_CREATED)
async def update_software_by_id(id: int, item: SoftwareUpdate, user: UserTable = Depends(developer_user)):
    return await update_software(id, item)


@router.delete("/{id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_software_by_id(id: int, user: UserTable = Depends(developer_user)):
    await delete_software(id)

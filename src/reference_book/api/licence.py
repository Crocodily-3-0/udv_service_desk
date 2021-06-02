from fastapi import APIRouter, Depends, status, Response
from ..schemas import Licence, LicenceCreate, LicenceDB, LicenceUpdate, LicencePage
from ..services import get_licence, add_licence, update_licence, delete_licence, get_licence_page
from ...users.models import UserTable
from ...users.logic import developer_user

router = APIRouter()


@router.get("/", response_model=LicencePage, status_code=status.HTTP_200_OK)
async def licence_list(last_id: int = 0, limit: int = 9, user: UserTable = Depends(developer_user)):
    if user.is_superuser:
        return await get_licence_page(last_id, limit)
    return None


@router.get('/{id}', response_model=Licence, status_code=status.HTTP_200_OK)
async def licence(id: int, user: UserTable = Depends(developer_user)):
    return await get_licence(id)


@router.post("/", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def create_licence(licence: LicenceCreate, user: UserTable = Depends(developer_user)):
    return await add_licence(licence)


@router.patch("/{id}", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def update_licence_by_id(id: int, item: LicenceUpdate, user: UserTable = Depends(developer_user)):
    return await update_licence(id, item)


@router.delete("/{id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_licence_by_id(id: int, user: UserTable = Depends(developer_user)):
    await delete_licence(id)

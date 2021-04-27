from typing import List

from fastapi import APIRouter, Depends, status, Response
from ..schemas import Licence, LicenceCreate, LicenceDB
from ..services import get_licence, get_licences, \
    get_client_licences, get_client_licence, add_client_licence, update_client_licence, delete_client_licence
from ...users.models import UserTable
from ...users.logic import developer_user

router = APIRouter()
for_client_router = APIRouter()


@router.get("/", response_model=List[LicenceDB], status_code=status.HTTP_200_OK)
async def licence_list(user: UserTable = Depends(developer_user)):
    return await get_licences()


@router.get('/{id}', response_model=Licence, status_code=status.HTTP_200_OK)
async def licence(id: int, user: UserTable = Depends(developer_user)):
    return await get_licence(id)


@for_client_router.get("/{id}/licences", response_model=List[LicenceDB], status_code=status.HTTP_200_OK)
async def client_licence_list(id: int, user: UserTable = Depends(developer_user)):
    return await get_client_licences(id)


@for_client_router.get('/{id}/licences/{pk}', response_model=Licence, status_code=status.HTTP_200_OK)
async def client_licence(id: int, pk: int, user: UserTable = Depends(developer_user)):
    return await get_client_licence(id, pk)


@for_client_router.post("/{id}/licences/", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def create_client_licence(id: int, licence: LicenceCreate, user: UserTable = Depends(developer_user)):
    return await add_client_licence(id, licence)


@for_client_router.put("/{id}/licences/{pk}", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def update_client_licence_by_id(id: int, pk: int, item: LicenceCreate, user: UserTable = Depends(developer_user)):
    return await update_client_licence(id, pk, item)


@for_client_router.delete("/{id}/licences/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_licence_by_id(id: int, pk: int, user: UserTable = Depends(developer_user)):
    await delete_client_licence(id, pk)

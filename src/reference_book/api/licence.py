from typing import List

from fastapi import APIRouter, status
from ..schemas import Licence, LicenceShort, LicenceCreate, LicenceDB
from ..services import get_licence, get_licences, add_licence, delete_licence, update_licence

router = APIRouter()


@router.get("/", response_model=List[LicenceShort], status_code=status.HTTP_200_OK)
async def licence_list():
    return await get_licences()


@router.get('/{id}', response_model=Licence, status_code=status.HTTP_200_OK)
async def licence(id: int):
    return await get_licence(id)


@router.post("/", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def create_licence(licence: LicenceCreate):
    return await add_licence(licence)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_licence_by_id(id: int):
    return await delete_licence(id)


@router.put("/{id}", response_model=LicenceDB, status_code=status.HTTP_201_CREATED)
async def update_licence_by_id(id: int, item: LicenceCreate):
    return await update_licence(id, item)

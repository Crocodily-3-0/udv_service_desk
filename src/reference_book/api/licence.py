from typing import List

from fastapi import APIRouter
from ..schemas import Licence, LicenceShort, LicenceCreate
from ..services import get_licence, get_licences, add_licence, delete_licence, update_licence

router = APIRouter()


@router.get("/", response_model=List[LicenceShort])
async def licence_list():
    return await get_licences()


@router.get('/{id}', response_model=Licence)
async def licence(id: int):
    return await get_licence(id)


@router.post("/")
async def create_licence(licence: LicenceCreate):
    return await add_licence(licence)


@router.delete("/{id}")
async def delete_licence(id: int):
    return await delete_licence(id)


@router.put("/{id}")
async def update_licence(id: int, item: LicenceCreate):
    return await update_licence(id, item)

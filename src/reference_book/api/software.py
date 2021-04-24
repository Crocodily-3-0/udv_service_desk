from typing import List

from fastapi import APIRouter
from ..services import get_software, get_softwares, get_software_with_modules, \
    add_software, delete_software, update_software
from ..schemas import Software, SoftwareShort, SoftwareCreate

router = APIRouter()


@router.get('/', response_model=List[SoftwareShort])
async def software_list():
    return await get_softwares()


@router.get('/{id}', response_model=SoftwareShort)
async def software(id: int):
    return await get_software(id)


@router.get("/{id}/modules", response_model=Software)
async def get_software_modules(id: int):
    return await get_software_with_modules(id)


@router.post("/")
async def create_licence(software: SoftwareCreate):
    return await add_software(software)


@router.delete("/{id}")
async def delete_software(id: int):
    return await delete_software(id)


@router.put("/{id}")
async def update_software(id: int, item: SoftwareCreate):
    return await update_software(id, item)

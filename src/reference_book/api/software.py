from typing import List

from fastapi import APIRouter, status

from ..services import get_software, get_softwares, get_software_with_modules, \
    add_software, delete_software, update_software
from ..schemas import Software, SoftwareShort, SoftwareCreate

router = APIRouter()


@router.get('/', response_model=List[SoftwareShort], status_code=status.HTTP_200_OK)
async def software_list():
    return await get_softwares()


@router.get('/{id}', response_model=SoftwareShort, status_code=status.HTTP_200_OK)
async def software(id: int):
    return await get_software(id)


@router.get("/{id}/modules", response_model=Software, status_code=status.HTTP_200_OK)
async def get_software_modules(id: int):
    return await get_software_with_modules(id)


@router.post("/", response_model=SoftwareShort, status_code=status.HTTP_201_CREATED)
async def create_software(software: SoftwareCreate):
    return await add_software(software)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_software_by_id(id: int):
    return await delete_software(id)


@router.put("/{id}", response_model=SoftwareShort, status_code=status.HTTP_201_CREATED)
async def update_software_by_id(id: int, item: SoftwareCreate):
    return await update_software(id, item)

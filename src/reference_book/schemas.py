from datetime import datetime
from typing import List

from pydantic import BaseModel

# from src.client_account.schemas import ClientDB


class SoftwareBase(BaseModel):
    name: str = ''


class SoftwareCreate(SoftwareBase):
    pass


class SoftwareDB(SoftwareBase):
    id: int

    class Config:
        orm_mode = True


class LicenceBase(BaseModel):
    number: int
    count_members: int
    date_end: datetime


class LicenceCreate(LicenceBase):
    software_id: int


# class LicenceShort(LicenceBase):
#     id: int
#     client_id: int
#     software_id: int  # TODO заменить на str


class LicenceDB(LicenceBase):
    id: int
    client_id: int
    software_id: int


class Licence(LicenceBase):
    id: int
    client_id: int  # TODO заменить на Client
    software: SoftwareDB


class ModuleBase(BaseModel):
    name: str


class ModuleCreate(ModuleBase):
    pass


class ModuleDB(ModuleBase):
    id: int
    software_id: int


class Module(ModuleBase):
    id: int
    software: SoftwareDB


class ModuleShort(ModuleBase):
    id: int


class Software(SoftwareBase):
    id: int
    modules: List[ModuleShort] = None

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.client_account.schemas import ClientShort


class SoftwareBase(BaseModel):
    name: str = ''


class SoftwareCreate(SoftwareBase):
    pass


class SoftwareShort(SoftwareBase):
    id: int

    class Config:
        orm_mode = True


class LicenceBase(BaseModel):
    number: int
    count_members: int
    date_end: datetime


class LicenceCreate(LicenceBase):
    client_id: int
    software_id: int


class LicenceShort(LicenceBase):
    id: int
    client_id: int  # TODO заменить на Client
    software_id: int  # TODO заменить на str

    class Config:
        orm_mode = True


class LicenceDB(LicenceBase):
    id: int
    client_id: int
    software_id: int


class Licence(LicenceBase):
    id: int
    client_id: ClientShort
    software: SoftwareShort

    class Config:
        orm_mode = True


class ModuleBase(BaseModel):
    name: str


class ModuleCreate(ModuleBase):
    software_id: int


class ModuleDB(ModuleBase):
    id: int
    software_id: int


class Module(ModuleBase):
    id: int
    software: SoftwareShort

    class Config:
        orm_mode = True


class ModuleShort(ModuleBase):
    id: int

    class Config:
        orm_mode = True


class Software(SoftwareBase):
    id: int
    modules: List[ModuleShort] = None

    class Config:
        orm_mode = True

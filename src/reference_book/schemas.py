from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ModuleBase(BaseModel):
    name: str


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(ModuleBase):
    pass


class ModuleDB(ModuleBase):
    id: int


class SoftwareBase(BaseModel):
    name: str = ''


class SoftwareCreate(SoftwareBase):
    pass


class SoftwareWithModulesCreate(SoftwareCreate):
    modules: List[int]


class SoftwareUpdate(SoftwareBase):
    pass


class SoftwareDB(SoftwareBase):
    id: int


class Software(SoftwareBase):
    id: int
    modules: List[ModuleDB]


class SoftwarePage(BaseModel):
    software_list: List[Software]
    modules_list: List[ModuleDB]


class LicenceBase(BaseModel):
    count_members: int
    date_end: datetime


class LicenceCreate(LicenceBase):
    number: int
    software_id: int


class LicenceUpdate(LicenceBase):
    count_members: Optional[int]
    date_end: Optional[datetime]


class LicenceDB(LicenceBase):
    id: int
    number: int
    software_id: int


class Licence(LicenceBase):
    id: int
    number: int
    closed_vacancies: int = -1
    software: SoftwareDB


class LicencePage(BaseModel):
    licences_list: List[Licence]
    software_list: List[SoftwareDB]


class EmployeeLicenceBase(BaseModel):
    pass


class EmployeeLicenceCreate(EmployeeLicenceBase):
    employee_id: str
    licence_id: int


class EmployeeLicenceUpdate(EmployeeLicenceBase):
    licence_id: int


class EmployeeLicenceDB(EmployeeLicenceBase):
    id: int
    employee_id: str
    licence_id: int


class EmployeeLicence(EmployeeLicenceBase):
    id: int
    employee_id: str
    licence: LicenceDB


class ClientLicenceBase(BaseModel):
    pass


class ClientLicenceCreate(EmployeeLicenceBase):
    client_id: int
    licence_id: int


class ClientLicenceUpdate(EmployeeLicenceBase):
    licence_id: int


class ClientLicenceDB(EmployeeLicenceBase):
    id: int
    client_id: int
    licence_id: int


class ClientLicence(EmployeeLicenceBase):
    id: int
    client_id: int
    licence: LicenceDB


class SoftwareModulesBase(BaseModel):
    software_id: int
    module_id: int


class SoftwareModulesCreate(SoftwareModulesBase):
    pass


class SoftwareModulesDB(SoftwareModulesBase):
    id: int

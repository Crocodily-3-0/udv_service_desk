from typing import List

from pydantic.main import BaseModel


class SoftwareStatistics(BaseModel):
    name: str
    count_appeals: int


class ModuleStatistics(BaseModel):
    name: str
    count_appeals: int


class StatusStatistics(BaseModel):
    name: str
    count_appeals: int


class AppealsStatistics(BaseModel):
    software_list: List[SoftwareStatistics]
    modules_list: List[ModuleStatistics]
    statuses_list: List[StatusStatistics]


class ClientStatistics(BaseModel):
    name: str
    count_appeals: int
    open_statuses: int
    closed: int
    canceled: int


class ClientsStatistics(BaseModel):
    clients_list: List[ClientStatistics]


class DeveloperStatistics(BaseModel):
    name: str
    count_appeals: int
    open_statuses: int
    closed_statuses: int


class DevelopersStatistics(BaseModel):
    developers_list: List[DeveloperStatistics]


class StatusesDistribution(BaseModel):
    new: int
    registered: int
    in_work: int
    closed: int
    canceled: int
    reopen: int

from datetime import datetime

from .schemas import ModuleCreate, LicenceCreate, LicenceShort, SoftwareCreate
from ..client_account.services import get_client
from ..db.db import database
from .models import softwares, modules, licences
from sqlalchemy.sql import select


async def get_softwares():
    result = await database.fetch_all(query=softwares.select())
    return [dict(software) for software in result]


async def get_software(id: int):
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == id))
    if result is not None:
        return dict(result)
    return None


async def add_software(software: SoftwareCreate):
    query = softwares.insert().values(**software.dict())
    id = await database.execute(query)
    return {**software.dict(), "id": id}


async def add_licence(licence: LicenceCreate):
    query = licences.insert().values(**licence.dict())
    id = await database.execute(query)
    return {**licence.dict(), "id": id}


async def add_module(module: ModuleCreate):
    query = modules.insert().values(**module.dict())
    id = await database.execute(query)
    return {**module.dict(), "id": id}


async def get_software_with_modules(id: int):
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == id))
    query = select([modules.c.id, modules.c.name]).select_from(modules).where(modules.c.software_id == id)
    module = await database.fetch_all(query)
    if result is not None:
        result = dict(result)
        module = [dict(m) for m in module]
        return {**result, "modules": module}
    return None


async def get_modules():
    result = await database.fetch_all(query=modules.select())
    return [dict(module) for module in result]


async def get_module(id: int):
    result = await database.fetch_one(query=modules.select().where(modules.c.id == id))
    if result is not None:
        module = dict(result)
        software = await get_software(module["software_id"])
        return {**module, "software": software}
    return None


async def get_licences():
    result = await database.fetch_all(query=licences.select())
    return [dict(licence) for licence in result]


async def get_licence(id: int):
    result = await database.fetch_one(query=licences.select().where(licences.c.id == id))
    if result is not None:
        licence = dict(result)
        # client = await get_client(licence["client_id"])
        software = await get_software(licence["software_id"])
        return {**licence, "software": software}
    return None


async def update_module(id: int, module: ModuleCreate):
    query = modules.update().where(modules.c.id == id).values(**module.dict())
    id_result = await database.execute(query)
    return id_result


async def update_licence(id: int, licence: LicenceCreate):
    query = licences.update().where(licences.c.id == id).values(**licence.dict())
    return await database.execute(query)


async def update_software(id: int, software: SoftwareCreate):
    query = softwares.update().where(softwares.c.id == id).values(**software.dict())
    return await database.execute(query)


async def delete_module(id: int):
    query = modules.delete().where(modules.c.id == id)
    result = await database.execute(query)
    return result


async def delete_licence(id: int):
    query = licences.delete().where(licences.c.id == id)
    return await database.execute(query)


async def delete_software(id: int):
    query = softwares.delete().where(softwares.c.id == id)
    return await database.execute(query)

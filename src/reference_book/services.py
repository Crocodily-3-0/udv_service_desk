from .schemas import ModuleCreate, LicenceCreate, SoftwareCreate
from ..db.db import database
from .models import softwares, modules, licences
from ..accounts.client_account.services import activate_client


async def get_softwares():
    result = await database.fetch_all(query=softwares.select())
    return [dict(software) for software in result]


async def get_software(id: int):
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == id))
    if result is not None:
        return dict(result)
    return None


async def get_software_with_modules(id: int):
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == id))
    if result is not None:
        result = dict(result)
        module = await get_software_modules(id)
        return {**result, "modules": module}
    return None


async def add_software(software: SoftwareCreate):
    query = softwares.insert().values(**software.dict())
    id = await database.execute(query)
    return {"id": id, **software.dict()}


async def update_software(id: int, software: SoftwareCreate):
    query = softwares.update().where(softwares.c.id == id).values(**software.dict())
    await database.execute(query)
    return {"id": id, **software.dict()}


async def delete_software(id: int):
    query = softwares.delete().where(softwares.c.id == id)
    await database.execute(query)


async def get_modules():
    result = await database.fetch_all(query=modules.select())
    return [dict(module) for module in result]


async def get_software_modules(id: int):
    result = await database.fetch_all(query=modules.select().where(modules.c.software_id == id))
    return [dict(module) for module in result]


async def get_module(id: int, pk: int):
    query = modules.select().where((modules.c.software_id == id) & (modules.c.id == pk))
    result = await database.fetch_one(query=query)
    if result is not None:
        module = dict(result)
        software = await get_software(id)
        return {**module, "software": software}
    return None


async def get_module_db(id: int):
    return dict(await database.fetch_one(modules.select().where(modules.c.id == id)))


async def add_module(id: int, module: ModuleCreate):
    query = modules.insert().values({**module.dict(), "software_id": id})
    module_id = await database.execute(query)
    return {"id": module_id, **module.dict(), "software_id": id}


async def update_module(id: int, pk: int, module: ModuleCreate):
    query = modules.update().where((modules.c.software_id == id) & (modules.c.id == pk)).values(**module.dict())
    await database.execute(query)
    return {"id": pk, **module.dict(), "software_id": id}


async def delete_module(id: int, pk: int):
    query = modules.delete().where((modules.c.software_id == id) & (modules.c.id == pk))
    await database.execute(query)


async def get_licences():
    result = await database.fetch_all(query=licences.select())
    return [dict(licence) for licence in result]


async def get_licence(id: int):
    result = await database.fetch_one(query=licences.select().where(licences.c.id == id))
    if result is not None:
        licence = dict(result)
        software = await get_software(licence["software_id"])
        return {**licence, "software": software}
    return None


async def get_client_licences(id: int):
    result = await database.fetch_all(query=licences.select().where(licences.c.client_id == id))
    return [dict(licence) for licence in result]


async def get_client_licence(id: int, pk: int):
    query = licences.select().where((licences.c.client_id == id) & (licences.c.id == pk))
    result = await database.fetch_one(query=query)
    if result is not None:
        licence = dict(result)
        software = await get_software(licence["software_id"])
        return {**licence, "software": software}
    return None


async def add_licence(licence: LicenceCreate):
    item = {**licence.dict()}
    query = licences.insert().values(item)
    licence_id = await database.execute(query)
    await activate_client(item["client_id"])
    return {"id": licence_id, **licence.dict()}


async def update_licence(pk: int, licence: LicenceCreate):
    query = licences.update().where(licences.c.id == pk).values(**licence.dict())
    await database.execute(query)
    return {"id": pk, **licence.dict()}


async def delete_licence(pk: int):
    query = licences.delete().where(licences.c.id == pk)
    await database.execute(query)


async def add_client_licence(id: int, licence: LicenceCreate):
    item = {**licence.dict(), "client_id": id}
    query = licences.insert().values(item)
    licence_id = await database.execute(query)
    await activate_client(id)
    return {"id": licence_id, **licence.dict(), "client_id": id}


async def update_client_licence(id: int, pk: int, licence: LicenceCreate):
    query = licences.update().where((licences.c.client_id == id) & (licences.c.id == pk)).values(**licence.dict())
    await database.execute(query)
    return {"id": pk, **licence.dict(), "client_id": id}


async def delete_client_licence(id: int, pk: int):
    query = licences.delete().where((licences.c.client_id == id) & (licences.c.id == pk))
    await database.execute(query)

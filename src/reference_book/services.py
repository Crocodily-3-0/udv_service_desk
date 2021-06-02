from fastapi import HTTPException, status

from .schemas import ModuleCreate, LicenceCreate, SoftwareCreate, EmployeeLicenceCreate, EmployeeLicenceUpdate, \
    SoftwareUpdate, SoftwareDB, Software, ModuleDB, ModuleUpdate, LicenceDB, Licence, LicenceUpdate, \
    EmployeeLicenceDB, SoftwareModulesCreate, SoftwareModulesDB, SoftwarePage, \
    SoftwareWithModulesCreate, LicencePage, ClientLicenceDB, ClientLicenceCreate
from ..accounts.client_account.models import clients
from ..accounts.client_account.schemas import ClientDB
from ..db.db import database
from .models import softwares, modules, licences, employee_licences, software_modules, client_licences
from ..errors import Errors
from typing import List, Optional


async def get_software_list(last_id: int = 0, limit: int = 9) -> List[Software]:
    query = softwares.select().where(softwares.c.id > last_id).limit(limit)
    result = await database.fetch_all(query=query)
    list_of_software = []
    for software in result:
        software = dict(software)
        module = await get_software_modules(software["id"])
        list_of_software.append(Software(**dict({**software, "modules": module})))
    return list_of_software


async def get_software_db_list() -> List[SoftwareDB]:
    result = await database.fetch_all(query=softwares.select())
    return [SoftwareDB(**dict(software)) for software in result]


async def get_software_page(last_id: int = 0, limit: int = 9) -> SoftwarePage:
    software_list = await get_software_list(last_id, limit)
    modules_list = await get_modules_db()
    return SoftwarePage(**dict({"software_list": software_list, "modules_list": modules_list}))


async def get_software(software_id: int) -> Optional[SoftwareDB]:
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == software_id))
    if result is not None:
        return SoftwareDB(**dict(result))
    return None


async def get_software_by_name(software_name: str) -> Optional[SoftwareDB]:
    result = await database.fetch_one(query=softwares.select().where(softwares.c.name == software_name))
    if result:
        return SoftwareDB(**dict(result))
    return None


async def get_software_with_modules(software_id: int) -> Optional[Software]:
    result = await database.fetch_one(query=softwares.select().where(softwares.c.id == software_id))
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.SOFTWARE_IS_NOT_EXIST
        )
    module = await get_software_modules(software_id)
    return Software(**dict({**dict(result), "modules": module}))


async def add_software(software: SoftwareCreate) -> SoftwareDB:
    if await get_software_by_name(software.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.SOFTWARE_IS_EXIST,
        )
    query = softwares.insert().values(**software.dict())
    software_id = await database.execute(query)
    return SoftwareDB(**dict({"id": software_id, **software.dict()}))


async def add_software_with_modules(software_with_modules: SoftwareWithModulesCreate) -> SoftwareDB:
    software = await add_software(SoftwareCreate(name=software_with_modules.name))
    modules_list = software_with_modules.modules
    for module_id in modules_list:
        try:
            module = await add_software_module(software.id, module_id)
        except Exception as e:
            print(e)
    return software


async def update_software(software_id: int, software: SoftwareUpdate) -> SoftwareDB:
    if get_software(software_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.SOFTWARE_IS_NOT_EXIST,
        )
    query = softwares.update().where(softwares.c.id == software_id).values(**software.dict())
    await database.execute(query)
    return SoftwareDB(**dict({"id": software_id, **software.dict()}))


async def delete_software(software_id: int) -> None:
    if get_software(software_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.SOFTWARE_IS_NOT_EXIST,
        )
    query = softwares.delete().where(softwares.c.id == software_id)
    await database.execute(query)


async def get_software_module(software_id: int, module_id: int) -> Optional[SoftwareModulesDB]:
    query = software_modules.select(). \
        where((software_modules.c.software_id == software_id) & (software_modules.c.module_id == module_id))
    result = await database.fetch_one(query=query)
    if result:
        return SoftwareModulesDB(**dict(result))
    return None


async def get_software_modules(software_id: int) -> List[ModuleDB]:
    query = software_modules.select().where(software_modules.c.software_id == software_id)
    result = await database.fetch_all(query=query)
    return [await get_module(software_module.module_id) for software_module in result]


async def add_software_module(software_id: int, module_id: int) -> SoftwareModulesDB:
    if await get_software_module(software_id, module_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.MODULE_FOR_THIS_SOFTWARE_IS_EXIST,
        )
    if await get_module(module_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.MODULE_IS_NOT_EXIST,
        )
    software_module = SoftwareModulesCreate(**dict({"software_id": software_id, "module_id": module_id}))
    query = software_modules.insert().values(software_module.dict())
    software_module_id = await database.execute(query)
    return SoftwareModulesDB(**dict({"id": software_module_id, **software_module.dict()}))


async def delete_software_module(software_id: int, module_id: int) -> None:
    if await get_software_module(software_id, module_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.MODULE_FOR_THIS_SOFTWARE_IS_NOT_EXIST,
        )
    query = software_modules.delete(). \
        where((software_modules.c.software_id == software_id) & (software_modules.c.module_id == module_id))
    await database.execute(query)


async def get_modules_db() -> List[ModuleDB]:
    result = await database.fetch_all(query=modules.select())
    return [ModuleDB(**dict(module)) for module in result]


async def get_modules(last_id: int = 0, limit: int = 9) -> List[ModuleDB]:
    query = modules.select().where(modules.c.id > last_id).limit(limit)
    result = await database.fetch_all(query=query)
    modules_list = []
    for module in result:
        modules_list.append(ModuleDB(**dict(module)))
    return modules_list


async def get_module(module_id: int) -> Optional[ModuleDB]:
    result = await database.fetch_one(query=modules.select().where(modules.c.id == module_id))
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.MODULE_IS_NOT_EXIST,
        )
    return ModuleDB(**dict(result))


async def get_module_by_name(module_name: str) -> Optional[ModuleDB]:
    result = await database.fetch_one(query=modules.select().where(modules.c.name == module_name))
    if result is not None:
        return ModuleDB(**dict(result))
    return None


async def add_module(module: ModuleCreate) -> ModuleDB:
    if await get_module_by_name(module.name) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.MODULE_IS_EXIST,
        )
    query = modules.insert().values(**module.dict())
    module_id = await database.execute(query)
    return ModuleDB(**dict({"id": module_id, **module.dict()}))


async def update_module(module_id: int, module: ModuleUpdate) -> ModuleDB:
    if await get_module(module_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.MODULE_IS_NOT_EXIST,
        )
    query = modules.update().where(modules.c.id == module_id).values(**module.dict())
    await database.execute(query)
    return ModuleDB(**dict({"id": module_id, **module.dict()}))


async def delete_module(module_id: int) -> None:
    if await get_module(module_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.MODULE_IS_NOT_EXIST,
        )
    query = modules.delete().where(modules.c.id == module_id)
    await database.execute(query)


async def get_licences_db() -> List[LicenceDB]:
    result = await database.fetch_all(query=licences.select())
    licences_list = []
    for licence in result:
        licences_list.append(LicenceDB(**dict(licence)))
    return licences_list


async def get_licences(last_id: int = 0, limit: int = 9) -> List[Licence]:
    query = licences.select().where(licences.c.id > last_id).limit(limit)
    result = await database.fetch_all(query=query)
    licences_list = []
    for licence in result:
        licence = dict(licence)
        software = await get_software(licence["software_id"])
        closed_vacancies = await get_count_employee_for_licence_id(licence["id"])
        licences_list.append(Licence(**dict({**licence, "software": software, "closed_vacancies": closed_vacancies})))
    return licences_list


async def get_licence_page(last_id: int = 0, limit: int = 9) -> LicencePage:
    licences_list = await get_licences(last_id, limit)
    software_list = await get_software_db_list()
    return LicencePage(**dict({"licences_list": licences_list, "software_list": software_list}))


async def get_licence(licence_id: int) -> Optional[Licence]:
    result = await database.fetch_one(query=licences.select().where(licences.c.id == licence_id))
    if result is not None:
        licence = dict(result)
        software = await get_software(licence["software_id"])
        closed_vacancies = await get_count_employee_for_licence_id(licence["id"])
        return Licence(**dict({**licence, "software": software, "closed_vacancies": closed_vacancies}))
    return None


async def get_licence_db(licence_id: int) -> Optional[LicenceDB]:
    result = await database.fetch_one(licences.select().where(licences.c.id == licence_id))
    if result:
        return LicenceDB(**dict(result))
    return None


async def get_licence_by_number(licence_number: int) -> Optional[LicenceDB]:
    result = await database.fetch_one(licences.select().where(licences.c.number == int(licence_number)))
    if result:
        return LicenceDB(**dict(result))
    return None


async def add_licence(licence: LicenceCreate) -> LicenceDB:
    if await get_licence_by_number(licence.number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.LICENCE_IS_EXIST,
        )
    if await get_software(licence.software_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.SOFTWARE_IS_NOT_EXIST,
        )
    query = licences.insert().values(licence.dict())
    licence_id = await database.execute(query)
    return LicenceDB(**dict({"id": licence_id, **licence.dict()}))


async def update_licence(licence_id: int, licence: LicenceUpdate) -> LicenceDB:
    old_licence = await get_licence_db(licence_id)
    if old_licence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.LICENCE_IS_NOT_EXIST,
        )
    licence = dict(licence)
    old_licence = dict(old_licence)
    for field in licence:
        if licence[field]:
            old_licence[field] = licence[field]
    query = licences.update().where(licences.c.id == licence_id).values(**old_licence)
    result = await database.execute(query=query)
    return await get_licence_db(licence_id)


async def delete_licence(licence_id: int) -> None:
    if await get_licence_db(licence_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.LICENCE_IS_NOT_EXIST,
        )
    query = licences.delete().where(licences.c.id == licence_id)
    await database.execute(query)


async def get_count_employee_for_licence_id(licence_id: int) -> int:
    query = employee_licences.select().where(employee_licences.c.licence_id == licence_id)
    result = await database.fetch_all(query=query)
    return len(result)


async def get_free_vacancy_in_licence(licence_id: int) -> int:
    licence = await get_licence_db(licence_id)
    count_employees = await get_count_employee_for_licence_id(licence_id)
    if licence is not None:
        return licence.count_members - count_employees
    return 0


async def get_employee_licence(employee_id: str) -> Optional[LicenceDB]:
    query = employee_licences.select().where(employee_licences.c.employee_id == employee_id)
    result = await database.fetch_one(query=query)
    if result:
        employee_licence = dict(result)
        licence = await get_licence_db(employee_licence["licence_id"])
        return licence
    return None


async def add_employee_licence(employee_id: str, licence_id: int) -> EmployeeLicenceDB:
    if await get_employee_licence(str(employee_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.USER_HAS_ANOTHER_LICENCE,
        )
    if await get_licence_db(licence_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.LICENCE_IS_NOT_EXIST,
        )
    if await get_free_vacancy_in_licence(licence_id) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.LICENCE_IS_FULL,
        )
    employee_licence = EmployeeLicenceCreate(**dict({"employee_id": str(employee_id), "licence_id": licence_id}))
    query = employee_licences.insert().values(**employee_licence.dict())
    employee_licence_id = await database.execute(query)
    return EmployeeLicenceDB(**dict({"id": employee_licence_id, **employee_licence.dict()}))


async def update_employee_licence(employee_id: str, licence_id: int) -> EmployeeLicenceDB:
    if await get_free_vacancy_in_licence(licence_id) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.LICENCE_IS_FULL,
        )
    employee_licence = EmployeeLicenceUpdate(**dict({"licence_id": licence_id}))
    query = employee_licences.update().where(employee_licences.c.employee_id == employee_id).values(
        **employee_licence.dict())
    employee_licence_id = await database.execute(query)
    return EmployeeLicenceDB(**dict({"id": employee_licence_id, "employee_id": employee_id, **employee_licence.dict()}))


async def get_client_licence(client_id: int, licence_id: int) -> Optional[ClientLicenceDB]:
    query = client_licences.select().\
        where((client_licences.c.client_id == client_id) & (client_licences.c.licence_id == licence_id))
    result = await database.fetch_one(query=query)
    if result:
        return ClientLicenceDB(**dict(result))
    return None


async def get_client_licences(client_id: int) -> List[Licence]:
    query = client_licences.select().where(client_licences.c.client_id == client_id)
    result = await database.fetch_all(query=query)
    client_licences_list = []
    for client_licence in result:
        client_licence = dict(client_licence)
        licence = dict(await get_licence_db(client_licence["licence_id"]))
        closed_vacancies = await get_count_employee_for_licence_id(client_licence["licence_id"])
        software = await get_software(licence["software_id"])
        client_licences_list.append(
            Licence(**dict({**licence, "closed_vacancies": closed_vacancies, "software": software})))
    return client_licences_list


async def add_client_licence(client_id: int, licence_id: int) -> ClientLicenceDB:
    if await get_client_licence(client_id, licence_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.CLIENT_HAS_THIS_LICENCE,
        )
    if await get_licence_db(licence_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.LICENCE_IS_NOT_EXIST,
        )
    client_licence = ClientLicenceCreate(**dict({"client_id": client_id, "licence_id": licence_id}))
    query = client_licences.insert().values(**client_licence.dict())
    employee_licence_id = await database.execute(query)
    client = await activate_client(client_id)
    return ClientLicenceDB(**dict({"id": employee_licence_id, **client_licence.dict()}))


async def activate_client(client_id: int) -> Optional[ClientDB]:
    current_client = await database.fetch_one(query=clients.select().where(clients.c.id == client_id))
    if current_client:
        current_client = dict(current_client)
        current_client["is_active"] = True
        await database.execute(query=clients.update().where(clients.c.id == client_id).values(**current_client))
    return current_client

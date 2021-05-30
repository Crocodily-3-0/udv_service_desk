from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from .schemas import ClientCreate, ClientUpdate, ClientAndOwnerCreate, ClientsPage, ClientShort, ClientPage, ClientDB, \
    Client, DevClientPage
from ...db.db import database
from .models import clients
from ...desk.models import appeals
from ...errors import Errors
from ...reference_book.schemas import LicenceDB
from ...reference_book.services import get_licences, add_client_licence, get_client_licences, get_software_db_list, \
    add_employee_licence, get_employee_licence
from ...users.logic import all_users, get_or_404, pre_update_user
from ...users.models import users
from ...users.schemas import UserCreate, OwnerCreate, UserUpdate, Employee, UserDB, EmployeeList
from ...service import send_mail


async def get_count_appeals(employee_id: UUID4) -> int:
    query = appeals.select().where(appeals.c.author_id == employee_id)
    result = await database.fetch_all(query=query)
    return len([dict(appeal) for appeal in result])


async def get_employees(client_id: int) -> List[EmployeeList]:
    result = await database.fetch_all(users.select().where(users.c.client_id == client_id))
    employees_list = []
    for employee in result:
        employee = dict(employee)
        licence: LicenceDB = await get_employee_licence(UUID4(employee["id"]))
        count_appeals: int = await get_count_appeals(UUID4(employee["id"]))
        employees_list.append(EmployeeList(**dict({**employee, "licence": licence, "count_appeals": count_appeals})))
    return employees_list


async def get_count_employees(client_id: int) -> int:
    result = await database.fetch_all(users.select().where(users.c.client_id == client_id))
    # result = [dict(employee) for employee in employees_data]
    return len(result)  # TODO проверить не будет ли ошибки


async def get_clients() -> List[ClientShort]:
    result = await database.fetch_all(clients.select())
    clients_list = []
    for client in result:
        client = dict(client)
        count_employees = await get_count_employees(client["id"])
        clients_list.append(ClientShort(**dict({**client, "count_employees": count_employees})))
    return clients_list


async def get_clients_page() -> ClientsPage:
    clients_list = await get_clients()
    licences_list = await get_licences()
    return ClientsPage(**dict({"clients_list": clients_list, "licences_list": licences_list}))


async def get_client_info(client_id: int) -> Client:
    client = await get_client(client_id)
    return client


async def get_client_page(client_id: int) -> ClientPage:
    client = await get_client(client_id)
    employees_list = await get_employees(client_id)
    licences_list = await get_client_licences(client_id)
    return ClientPage(**dict({**client,
                              "employees_list": employees_list,
                              "licences_list": licences_list}))


async def get_dev_client_page(client_id: int) -> DevClientPage:
    client = await get_client(client_id)
    employees_list = await get_employees(client_id)
    software_list = await get_software_db_list()
    return DevClientPage(**dict({**client,
                                 "employees_list": employees_list,
                                 "software_list": software_list}))


async def get_client(client_id: int) -> Optional[Client]:
    query = clients.select().where(clients.c.id == client_id)
    result = await database.fetch_one(query=query)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.CLIENT_NOT_FOUND)
    owner = await get_client_owner(client_id)
    licences_list = await get_client_licences(client_id)
    return Client(**dict({**dict(result),
                          "owner": owner,
                          "licences": licences_list}))


async def get_client_db(client_id: int) -> Optional[ClientDB]:
    query = clients.select().where(clients.c.id == client_id)
    client = await database.fetch_one(query=query)
    if client:
        return ClientDB(**dict(client))
    return None


async def add_client(data: ClientAndOwnerCreate) -> Optional[ClientDB]:
    client = ClientCreate(**data.dict())
    query = clients.insert().values({**client.dict(), "is_active": False, "owner_id": "undefined"})
    try:
        client_id = await database.execute(query)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.COMPANY_IS_EXIST,
        )
    for licence_id in data.licences_list:
        licence = await add_client_licence(client_id, licence_id)
    owner = OwnerCreate(
        email=data.email,
        password=data.password,
        name=data.owner_name,
        surname=data.surname,
        avatar=data.owner_avatar,
        client_id=client_id,
        is_owner=True,
        date_reg=datetime.utcnow(),
    )
    owner = await add_owner(client_id, owner)
    owner_licence = await add_employee_licence(owner.id, data.owner_licence)
    new_client = await get_client_db(client_id)
    return new_client


async def update_client(id: int, client: ClientUpdate) -> Optional[ClientDB]:  # TODO проверить работу обновления
    client_dict = client.dict()
    if "owner_id" in client_dict:
        client_dict["owner_id"] = str(client_dict["owner_id"])
    query = clients.update().where(clients.c.id == id).values(**client_dict)
    client_id = await database.execute(query)
    updated_client = await get_client_db(client_id)
    return updated_client


async def activate_client(id: int) -> Optional[ClientDB]:
    current_client = await database.fetch_one(query=clients.select().where(clients.c.id == id))
    if current_client:
        current_client = dict(current_client)
        current_client["is_active"] = True
        await database.execute(query=clients.update().where(clients.c.id == id).values(**current_client))
    return current_client


async def block_client(id: int) -> Optional[ClientDB]:
    current_client = await database.fetch_one(query=clients.select().where(clients.c.id == id))
    if current_client:
        current_client = dict(current_client)
        current_client["is_active"] = False
        await database.execute(query=clients.update().where(clients.c.id == id).values(**current_client))
    return current_client


async def get_client_owner(client_id: int) -> Employee:
    query = users.select().where((users.c.client_id == client_id) & (users.c.is_owner is True))
    owner = await database.fetch_one(query=query)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND
        )
    owner = dict(owner)
    licence: LicenceDB = await get_employee_licence(UUID4(owner["id"]))
    return Employee(**dict({**owner, "licence": licence}))


async def update_client_owner(client_id: int, new_owner_id: UUID4) -> Optional[UserDB]:
    client = await get_client_db(client_id)
    if client:
        if client.owner_id == "undefined":
            new_client = ClientUpdate(name=client.name, owner_id=str(new_owner_id))
            await update_client(client_id, new_client)
            new_owner = await get_or_404(new_owner_id)
        else:
            update_old = UserUpdate(is_owner=False)
            update_new = UserUpdate(is_owner=True)
            new_client = ClientUpdate(**dict(client), owner_id=new_owner_id)
            old_owner = await pre_update_user(UUID4(client.owner_id), update_old)
            new_owner = await pre_update_user(new_owner_id, update_new)
            client = await update_client(client_id, new_client)
        return new_owner
    return None


async def add_owner(client_id: int, owner: OwnerCreate):
    user = UserCreate(**owner.dict())
    try:
        created_owner = await all_users.create_user(user, safe=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )

    message = f"Добро пожаловать в UDV Service Desk!\n\nВаш логин в системе: {owner.email}\nВаш пароль: {owner.password}"
    await send_mail(owner.email, "Вы зарегистрированы в системе", message)
    updated_owner = await update_client_owner(client_id, created_owner.id)
    return updated_owner

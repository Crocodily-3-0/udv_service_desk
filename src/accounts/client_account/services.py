from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4
from sqlalchemy import desc

from .schemas import ClientCreate, ClientUpdate, ClientAndOwnerCreate, ClientsPage, ClientShort, ClientPage, ClientDB, \
    Client, DevClientPage
from ...db.db import database
from .models import clients
from ...desk.models import appeals
from ...errors import Errors
from ...reference_book.schemas import LicenceDB
from ...reference_book.services import add_client_licence, get_client_licences, get_software_db_list, \
    add_employee_licence, get_employee_licence, get_licences_db
from ...users.logic import all_users, get_or_404, pre_update_user, user_is_active, get_user_by_email, default_uuid
from ...users.models import users
from ...users.schemas import UserCreate, OwnerCreate, Employee, UserDB, EmployeeList, EmployeeUpdate
from ...service import send_mail, Email


async def get_count_appeals(employee_id: str) -> int:
    query = appeals.select().where(appeals.c.author_id == employee_id)
    result = await database.fetch_all(query=query)
    return len(result)


async def get_employees(client_id: int, last_id: UUID4 = default_uuid, limit: int = 9) -> List[EmployeeList]:
    query = users.select()\
        .where((users.c.client_id == client_id) & (users.c.id > str(last_id))).order_by(desc(users.c.id)).limit(limit)
    result = await database.fetch_all(query=query)
    employees_list = []
    for employee in result:
        employee = dict(employee)
        licence: LicenceDB = await get_employee_licence(str(employee["id"]))
        count_appeals: int = await get_count_appeals(str(employee["id"]))
        employees_list.append(EmployeeList(**dict({**employee, "licence": licence, "count_appeals": count_appeals})))
    return employees_list


async def get_count_employees(client_id: int) -> int:
    result = await database.fetch_all(users.select().where(users.c.client_id == client_id))
    return len(result)


async def get_clients_db() -> List[ClientDB]:
    result = await database.fetch_all(clients.select())
    return [ClientDB(**dict(client)) for client in result]


async def get_clients(last_id: int = 0, limit: int = 9) -> List[ClientShort]:
    query = clients.select().where(clients.c.id > last_id).limit(limit)
    result = await database.fetch_all(query=query)
    clients_list = []
    for client in result:
        client = dict(client)
        owner = await get_or_404(UUID4(client["owner_id"]))
        count_employees = await get_count_employees(client["id"])
        clients_list.append(ClientShort(**dict({**client,
                                                "owner": owner,
                                                "count_employees": count_employees})))
    return clients_list


async def get_clients_page(last_id: int = 0, limit: int = 9) -> ClientsPage:
    clients_list = await get_clients(last_id, limit)
    licences_list = await get_licences_db()
    return ClientsPage(**dict({"clients_list": clients_list, "licences_list": licences_list}))


async def get_client_info(client_id: int) -> Client:
    client = await get_client(client_id)
    return client


async def get_client_page(client_id: int, last_id: UUID4 = default_uuid, limit: int = 9) -> ClientPage:
    client = await get_client(client_id)
    employees_list = await get_employees(client_id, last_id, limit)
    licences_list = await get_client_licences(client_id)
    return ClientPage(**dict({"client": client,
                              "employees_list": employees_list,
                              "licences_list": licences_list}))


async def get_dev_client_page(client_id: int, last_id: UUID4 = default_uuid, limit: int = 9) -> DevClientPage:
    client = await get_client(client_id)
    employees_list = await get_employees(client_id, last_id, limit)
    software_list = await get_software_db_list()
    return DevClientPage(**dict({"client": client,
                                 "employees_list": employees_list,
                                 "software_list": software_list}))


async def get_client(client_id: int) -> Optional[Client]:
    query = clients.select().where(clients.c.id == client_id)
    client = await database.fetch_one(query=query)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.CLIENT_NOT_FOUND)
    client = dict(client)
    owner = await get_or_404(UUID4(str(client["owner_id"])))
    licences_list = await get_client_licences(client_id)
    return Client(**dict({**client,
                          "owner": owner,
                          "licences": licences_list}))


async def get_client_db(client_id: int) -> Optional[ClientDB]:
    query = clients.select().where(clients.c.id == client_id)
    client = await database.fetch_one(query=query)
    if client:
        return ClientDB(**dict(client))
    return None


async def add_client(data: ClientAndOwnerCreate) -> Optional[ClientDB]:
    client = ClientCreate(**dict(data))
    query = clients.insert().values({**client.dict(), "is_active": False, "owner_id": "undefined"})
    if await get_user_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Errors.COMPANY_IS_EXIST,
        )
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
        patronymic=data.patronymic,
        avatar=data.owner_avatar,
        client_id=client_id,
        is_owner=True,
        date_reg=datetime.utcnow(),
    )
    owner = await add_owner(client_id, owner)
    await add_employee_licence(str(owner.id), data.owner_licence)
    new_client = await get_client_db(client_id)
    return new_client


async def update_client(client_id: int, client: ClientUpdate) -> Optional[ClientDB]:
    new_client_dict = dict(client)
    old_client_dict = dict(await get_client_db(client_id))
    for field in new_client_dict:
        if new_client_dict[field]:
            old_client_dict[field] = new_client_dict[field]
    query = clients.update().where(clients.c.id == client_id).values(**old_client_dict)
    updated_client = await database.execute(query)
    updated_client = await get_client_db(client_id)
    return updated_client


async def block_client(client_id: int) -> Optional[ClientDB]:
    new_client = ClientUpdate(is_activa=False)
    updated_client = await update_client(client_id, new_client)
    return updated_client


async def get_client_owner(client_id: int) -> Employee:
    query = users.select().where((users.c.client_id == client_id) & (users.c.is_owner == 1))
    owner = await database.fetch_one(query=query)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND
        )
    owner = dict(owner)
    licence: LicenceDB = await get_employee_licence(str(owner["id"]))
    return Employee(**dict({**owner, "licence": licence}))


async def update_client_owner(client_id: int, new_owner_id: UUID4) -> Optional[UserDB]:
    client = await get_client_db(client_id)
    if client and await user_is_active(new_owner_id):
        new_client = ClientUpdate(owner_id=str(new_owner_id))
        if client.owner_id == "undefined":
            client = await update_client(client_id, new_client)
            new_owner = await get_or_404(new_owner_id)
        else:
            update_old = EmployeeUpdate(is_owner=False)
            update_new = EmployeeUpdate(is_owner=True)
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

    await send_mail_with_owner_pwd(owner)
    updated_owner = await update_client_owner(client_id, created_owner.id)
    return updated_owner


async def send_mail_with_owner_pwd(user: OwnerCreate) -> None:
    message = f"Добро пожаловать в UDV Service Desk!\n\n" \
              f"Ваш логин в системе: {user.email}\nВаш пароль: {user.password}"
    email = Email(recipient=user.email, title="Регистрация в UDV Service Desk", message=message)
    await send_mail(email)

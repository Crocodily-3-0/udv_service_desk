import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import HTTPException, status
from fastapi_users.router import ErrorCode
from pydantic.types import UUID4

from .schemas import ClientCreate, ClientUpdate, ClientAndOwnerCreate
from ..employee_account.services import update_employee
from ...db.db import database
from .models import clients
from ...errors import Errors
from ...reference_book.models import licences, softwares
from ...users.logic import all_users, get_or_404
from ...users.models import users
from ...users.schemas import UserCreate, OwnerCreate, UserUpdate
from ...service import check_dict


async def get_clients():
    result = await database.fetch_all(clients.select())
    return [dict(client) for client in result]


async def get_client(id: int):
    query = clients.select().where(clients.c.id == id)
    result = await database.fetch_one(query=query)
    if result:
        result = dict(result)
        owner_data = await database.fetch_one(query=users.select().where(users.c.id == result["owner_id"]))
        owner = await check_dict(owner_data)
        employee_data = await database.fetch_all(query=users.select().where(users.c.client_id == id))
        employees = [dict(employee) for employee in employee_data]
        licence_data = await database.fetch_all(query=licences.select().where(licences.c.client_id == id))
        licences_dict = [dict(licence) for licence in licence_data]
        software = [await database.fetch_one(
            softwares.select().where(softwares.c.id == licence["software_id"])
        ) for licence in licence_data]
        return {**result,
                "owner": owner,
                "employees": employees,
                "licences": licences_dict,
                "software": software}


async def get_client_db(client_id: int):
    query = clients.select().where(clients.c.id == client_id)
    client = await database.fetch_one(query=query)
    if client:
        return dict(client)
    return None


async def add_client(data: ClientAndOwnerCreate):
    client = ClientCreate(**data.dict())
    query = clients.insert().values({**client.dict(), "is_active": False, "owner_id": "undefined"})
    client_id = await database.execute(query)
    owner = OwnerCreate(
        email=data.email,
        password=data.password,
        name=data.owner_name,
        surname=data.surname,
        client_id=client_id,
        is_owner=True,
        date_reg=datetime.utcnow()
    )
    owner = await add_owner(client_id, owner)
    new_client = await get_client_db(client_id)
    return new_client


async def update_client(id: int, client: ClientUpdate):  # TODO проверить работу обновления
    client_dict = client.dict()
    if "owner_id" in client_dict:
        client_dict["owner_id"] = str(client_dict["owner_id"])
    query = clients.update().where(clients.c.id == id).values(**client_dict)
    client_id = await database.execute(query)
    updated_client = await get_client_db(client_id)
    print(updated_client)
    return updated_client


async def activate_client(id: int):
    current_client = await database.fetch_one(query=clients.select().where(clients.c.id == id))
    if current_client:
        current_client = dict(current_client)
        current_client["is_active"] = True
        await database.execute(query=clients.update().where(clients.c.id == id).values(**current_client))
    return None


async def get_client_owner(client_id: int):
    query = users.select().where((users.c.client_id == client_id) & (users.c.is_owner is True))
    owner = await database.fetch_one(query=query)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Errors.USER_NOT_FOUND
        )
    return dict(owner)


async def update_owner(client_id: int, new_owner_id: UUID4):
    client = await database.fetch_one(clients.select().where(clients.c.id == client_id))
    if client:
        client = dict(client)
        if client["owner_id"] == "undefined":
            # client["owner_id"] = new_owner_id
            new_client = ClientCreate(name=client["name"], owner_id=str(new_owner_id))
            await update_client(client_id, new_client)
            new_owner = await get_or_404(new_owner_id)
        else:
            update_old = UserUpdate(is_owner=False)
            update_new = UserUpdate(is_owner=True)
            new_client = ClientCreate(**client, owner_id=new_owner_id)
            old_owner = await update_employee(client["owner_id"], update_old)
            new_owner = await update_employee(new_owner_id, update_new)
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
    updated_owner = await update_owner(client_id, created_owner.id)
    return updated_owner

from .schemas import ClientCreate
from ..db.db import database
from .models import clients
from ..reference_book.models import licences
from ..users.models import users, UserTable


async def get_clients():
    result = await database.fetch_all(clients.select())
    return [dict(client) for client in result]


async def get_client(id: int):
    query = clients.select().where(clients.c.id == id)
    result = await database.fetch_one(query=query)
    if result:
        result = dict(result)
        owner = dict(await database.fetch_one(query=users.select().where(users.c.id == result["owner_id"])))
        employee_data = await database.fetch_all(query=users.select().where(users.c.client_id == id))
        employees = [dict(employee) for employee in employee_data]
        licence_data = await database.fetch_all(query=licences.select().where(licences.c.client_id == id))
        licences_dict = [dict(licence) for licence in licence_data]
        return {**result,
                "owner": owner,
                "employees": employees,
                "licences": licences_dict}


async def get_client_db(client_id):
    query = clients.select().where(clients.c.id == client_id)
    return dict(await database.fetch_one(query=query))


async def add_client(client: ClientCreate):
    query = clients.insert().values(client.dict())
    client_id = await database.execute(query)
    return await get_client_db(client_id)

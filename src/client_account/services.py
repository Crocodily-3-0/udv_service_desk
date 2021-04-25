from ..db.db import database
from .models import clients
from ..users.models import users


async def get_clients():
    result = await database.fetch_all(clients.select())
    return [dict(client) for client in result]


async def get_client(id: int):
    query = clients.select().where(clients.c.id == id)
    result = await database.fetch_one(query=query)
    if result:
        result = dict(result)
        query = users.select().where(users.c.id == result["owner_id"])
        owner = await database.fetch_one(query=query)
        return {**result, "owner": owner}

from ..db.db import database
from .models import appeals, comments
from ..reference_book.models import softwares, modules


async def get_appeals():
    result = await database.fetch_all(query=appeals.select())
    return [dict(appeal) for appeal in result]


async def get_appeal(id: int):
    query = appeals.select().where(appeals.c.id == id)
    appeal = await database.fetch_one(query=query)
    if appeal:
        appeal = dict(appeal)
        # author = await database.fetch_one(query=members.select().where(members.c.id == appeal["author"]))
        # responsible = await database.fetch_one(query=developers.select().where(developers.c.id == appeal["responsible"]))
        software = await database.fetch_one(query=softwares.select().where(softwares.c.id == appeal["software_id"]))
        module = await database.fetch_one(query=modules.select().where(modules.c.id == appeal["module_id"]))
        return {**appeal, "software": software, "module": module}
    return None


async def get_comments(id: int):
    query = comments.select().where(comments.c.appeal == id)
    result = await database.fetch_all(query)
    result = [dict(comment) for comment in result]
    return result


async def get_comment(id: int, pk: int):
    query = comments.select().where((comments.c.id == pk) & (comments.c.appeal == id))
    result = await database.fetch_one(query)
    if result:
        return dict(result)
    return None

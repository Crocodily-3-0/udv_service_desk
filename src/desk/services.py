from .schemas import AppealCreate, CommentCreate, AppealUpdate
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


async def add_appeal(appeal: AppealCreate):
    query = appeals.insert().values(**appeal.dict())
    id = await database.execute(query)
    return await get_appeal(id)


async def add_comment(appeal_id: int, comment: CommentCreate):
    query = comments.insert().values({**comment.dict(), "appeal_id": appeal_id})
    comment_id = await database.execute(query)
    return {**comment.dict(), "appeal_id": appeal_id, "id": comment_id}


async def update_appeal(id: int, appeal: AppealUpdate):
    query = appeals.update().where(appeals.c.id == id).values(**appeal.dict())
    id_result = await database.execute(query)
    return await get_appeal(id_result)


async def update_comment(id: int, comment: CommentCreate):
    query = comments.update().where(comments.c.id == id).values(**comment.dict())
    result = await database.execute(query)
    return result


async def delete_appeal(id: int):
    query = appeals.delete().where(appeals.c.id == id)
    result = await database.execute(query)
    return result


async def delete_comment(id: int):
    query = comments.delete().where(comments.c.id == id)
    result = await database.execute(query)
    return result

from .schemas import AppealCreate, CommentCreate, AppealUpdate, CommentUpdate
from ..accounts.client_account.models import clients
from ..db.db import database
from .models import appeals, comments
from ..reference_book.models import softwares, modules
from ..users.models import UserTable, users
from .models import StatusTasks


async def get_all_appeals():
    result = await database.fetch_all(query=appeals.select())
    return [dict(appeal) for appeal in result]


async def get_appeals(user: UserTable):
    query = appeals.select().where(appeals.c.client_id == user.client_id)
    result = await database.fetch_all(query=query)
    return [dict(appeal) for appeal in result]


async def get_appeal(id: int, user: UserTable):
    query = appeals.select().where((appeals.c.id == id) & (appeals.c.client_id == user.client_id))
    appeal = await database.fetch_one(query=query)
    if appeal:
        appeal = dict(appeal)
        # TODO сделать проверку на None
        client = dict(await database.fetch_one(query=clients.select().where(clients.c.id == appeal["client_id"])))
        author = dict(await database.fetch_one(query=users.select().where(users.c.id == appeal["author_id"])))
        responsible = await database.fetch_one(query=users.select().where(users.c.id == appeal["responsible_id"]))
        software = dict(await database.fetch_one(query=softwares.select().where(softwares.c.id == appeal["software_id"])))
        module = dict(await database.fetch_one(query=modules.select().where(modules.c.id == appeal["module_id"])))
        comment = await get_comments(id, user)
        return {**appeal,
                "client": client,
                "author": author,
                "responsible": responsible,
                "software": software,
                "module": module,
                "comment": comment}
    return None


async def get_appeal_db(id: int):
    query = appeals.select().where(appeals.c.id == id)
    result = await database.fetch_one(query=query)
    return dict(result)


async def add_appeal(appeal: AppealCreate, user: UserTable):
    item = {**appeal.dict(), "client_id": int(user.client_id), "author_id": str(user.id), "status": StatusTasks.new}  # TODO убрать статус, после того, как настрою default
    query = appeals.insert().values(item)
    appeal_id = await database.execute(query)
    return await get_appeal_db(appeal_id)


async def update_appeal(id: int, appeal: AppealUpdate, user: UserTable):
    query = appeals.update().\
        where((appeals.c.id == id) & (appeals.c.client_id == user.client_id)).\
        values(appeal.dict())
    result_id = await database.execute(query)
    return await get_appeal_db(result_id)


async def delete_appeal(id: int):
    query = appeals.delete().where(appeals.c.id == id)
    result = await database.execute(query)
    return result


async def get_comments(id: int, user: UserTable):
    # TODO проверка на пользователя имеющего доступ: (appeals.c.client_id == user.client_id)
    query = comments.select().where(comments.c.appeal_id == id)
    result = await database.fetch_all(query)
    result = [dict(comment) for comment in result]
    return result


async def get_comment(id: int, pk: int, user: UserTable):
    # TODO проверка на пользователя имеющего доступ: (appeals.c.client_id == user.client_id)
    query = comments.select().where((comments.c.id == pk) & (comments.c.appeal_id == id))
    comment = await database.fetch_one(query)
    if comment:
        comment = dict(comment)
        author = await database.fetch_one(query=users.select().where(users.c.id == comment["author_id"]))
        return {**comment, "author": author}
    return None


async def get_comment_db(id: int):
    query = comments.select().where(comments.c.id == id)
    return dict(await database.fetch_one(query=query))


async def add_comment(appeal_id: int, comment: CommentCreate, user: UserTable):
    # TODO проверка на пользователя имеющего доступ: (appeals.c.client_id == user.client_id)
    item = {**comment.dict(), "appeal_id": int(appeal_id), "author_id": str(user.id)}
    query = comments.insert().values(item)
    comment_id = await database.execute(query)
    return await get_comment_db(comment_id)


async def update_comment(id: int, comment: CommentUpdate, user: UserTable):
    query = comments.update().where((comments.c.id == id) & (comments.c.author_id == user.id)).values(**comment.dict())
    result_id = await database.execute(query)
    return await get_comment_db(result_id)


async def delete_comment(id: int, user: UserTable):
    query = comments.delete().where((comments.c.id == id) & (comments.c.author_id == str(user.id)))
    result = await database.execute(query)
    print(result)
    return result

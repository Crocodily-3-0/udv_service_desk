from datetime import datetime

from .schemas import AppealCreate, CommentCreate, AppealUpdate, CommentUpdate
from ..accounts.client_account.models import clients
from ..db.db import database
from .models import appeals, comments
from ..errors import Errors
from ..reference_book.models import softwares, modules
from ..users.logic import get_developers
from ..users.models import UserTable, users
from .models import StatusTasks
from ..service import check_dict

from fastapi import HTTPException, status


async def get_all_appeals():
    result = await database.fetch_all(query=appeals.select())
    return [dict(appeal) for appeal in result]


async def get_appeals(user: UserTable):
    query = appeals.select().where(appeals.c.client_id == user.client_id)
    result = await database.fetch_all(query=query)
    return [dict(appeal) for appeal in result]


async def get_appeal(id: int, user: UserTable):
    appeal = await check_access(id, user, status.HTTP_404_NOT_FOUND)
    client = await check_dict(await database.fetch_one(query=clients.select().where(clients.c.id == appeal["client_id"])))
    author = await check_dict(await database.fetch_one(query=users.select().where(users.c.id == appeal["author_id"])))
    responsible = await check_dict(
        await database.fetch_one(query=users.select().where(users.c.id == appeal["responsible_id"])))
    software = await check_dict(
        await database.fetch_one(query=softwares.select().where(softwares.c.id == appeal["software_id"])))
    module = await check_dict(await database.fetch_one(query=modules.select().where(modules.c.id == appeal["module_id"])))
    comment = await get_comments(id, user)
    result = {**appeal,
              "client": client,
              "author": author,
              "responsible": responsible,
              "software": software,
              "module": module,
              "comment": comment}
    if user.is_superuser:
        developers = await get_developers()
        allowed_statuses = await get_next_status(id, user)
        return {**result,
                "developers": developers,
                "allowed_statuses": allowed_statuses}
    return result


async def get_appeal_db(id: int):
    query = appeals.select().where(appeals.c.id == id)
    result = await database.fetch_one(query=query)
    if result:
        return dict(result)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def add_appeal(appeal: AppealCreate, user: UserTable):
    item = {**appeal.dict(), "client_id": int(user.client_id), "author_id": str(user.id), "status": StatusTasks.new}
    query = appeals.insert().values(item)
    appeal_id = await database.execute(query)
    return await get_appeal_db(appeal_id)


async def update_attachments(id: int, appeal: AppealUpdate, user: UserTable):
    # TODO сделать добавление вложений для пользователя
    pass


async def update_appeal(id: int, appeal: AppealUpdate, user: UserTable):
    old_appeal = await get_appeal_db(id)
    if old_appeal["status"] == StatusTasks.closed or old_appeal["status"] == StatusTasks.canceled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.APPEAL_IS_CLOSED)
    appeal = appeal.dict(exclude_unset=True)
    if "status" in appeal and (appeal["status"] == StatusTasks.closed or appeal["status"] == StatusTasks.canceled):
        appeal["date_processing"] = datetime.utcnow()
    if "responsible_id" in appeal and old_appeal["status"] == StatusTasks.new:
        appeal["status"] = StatusTasks.registered
    for field in appeal:
        old_appeal[field] = appeal[field]
    query = appeals.update().where(appeals.c.id == id).values(old_appeal)
    result_id = await database.execute(query)
    return await get_appeal_db(result_id)


async def delete_appeal(id: int):
    query = appeals.delete().where(appeals.c.id == id)
    result = await database.execute(query)
    return result


async def get_comments(id: int, user: UserTable):
    await check_access(id, user, status.HTTP_404_NOT_FOUND)
    query = comments.select().where(comments.c.appeal_id == id)
    result = await database.fetch_all(query)
    return [dict(comment) for comment in result]


async def get_comment(id: int, pk: int, user: UserTable):
    await check_access(id, user, status.HTTP_404_NOT_FOUND)
    query = comments.select().where((comments.c.id == pk) & (comments.c.appeal_id == id))
    comment = await database.fetch_one(query)
    if comment:
        comment = dict(comment)
        author = await database.fetch_one(query=users.select().where(users.c.id == comment["author_id"]))
        return {**comment, "author": author}
    return None


async def get_comment_db(id: int):
    query = comments.select().where(comments.c.id == id)
    result = await database.fetch_one(query=query)
    return await check_dict(result)


async def add_comment(appeal_id: int, comment: CommentCreate, user: UserTable):
    await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    item = {**comment.dict(), "appeal_id": int(appeal_id), "author_id": str(user.id)}
    query = comments.insert().values(item)
    comment_id = await database.execute(query)
    return await get_comment_db(comment_id)


async def update_comment(appeal_id: int, pk: int, comment: CommentUpdate, user: UserTable):
    await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    query = comments.update().where((comments.c.id == pk) & (comments.c.author_id == user.id)).values(**comment.dict())
    result_id = await database.execute(query)
    return await get_comment_db(result_id)


async def delete_comment(appeal_id: int, pk: int, user: UserTable):
    await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    query = comments.delete().where((comments.c.id == pk) & (comments.c.author_id == str(user.id)))
    await database.execute(query)


async def check_access(appeal_id: int, user: UserTable, status_code: status):
    appeal = await get_appeal_db(appeal_id)
    if appeal["client_id"] != user.client_id and not user.is_superuser:
        raise HTTPException(status_code=status_code)
    return appeal


async def get_next_status(appeal_id: int, user: UserTable):
    appeal = await get_appeal_db(appeal_id)
    current_status = appeal["status"]
    if user.is_superuser:
        if current_status is StatusTasks.new:
            return [StatusTasks.registered]
        elif current_status is StatusTasks.registered:
            return [StatusTasks.in_work]
        elif current_status is StatusTasks.in_work:
            return [StatusTasks.closed, StatusTasks.canceled]
    elif current_status is StatusTasks.closed or current_status is StatusTasks.canceled:
        return [StatusTasks.in_work]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.USER_CAN_NOT_CHANGE_STATUS)

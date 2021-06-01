import shutil
from datetime import datetime
from typing import List, Union, Optional

from pydantic.types import UUID4

from .schemas import AppealCreate, CommentCreate, AppealUpdate, CommentUpdate, AppealList, AppealDB, Appeal, DevAppeal, \
    AppealsPage, AttachmentDB, AttachmentCreate
from ..accounts.client_account.models import clients
from ..accounts.client_account.services import get_client_db, get_client
from ..db.db import database
from .models import appeals, comments, attachments
from ..errors import Errors
from ..reference_book.models import softwares, modules
from ..reference_book.services import get_software, get_module, get_modules, get_software_list, get_software_db_list
from ..users.logic import get_developers, get_or_404, get_user, get_client_users
from ..users.models import UserTable, users
from .models import StatusTasks
from ..service import check_dict, send_mail, Email

from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse


async def get_all_appeals() -> List[AppealList]:
    result = await database.fetch_all(query=appeals.select())
    appeals_list = []
    for appeal in result:
        appeal = dict(appeal)
        author = await get_or_404(appeal["author_id"])
        client = await get_client_db(appeal["client_id"])
        responsible = await get_or_404(appeal["responsible_id"])
        software = await get_software(appeal["software_id"])
        module = await get_module(appeal["module_id"])
        appeals_list.append(AppealList(**dict({
            **appeal,
            "author": author,
            "client": client,
            "responsible": responsible,
            "software": software,
            "module": module})))
    return appeals_list


async def get_appeals(user: UserTable) -> List[Appeal]:
    query = appeals.select().where(appeals.c.client_id == user.client_id)
    result = await database.fetch_all(query=query)
    appeals_list = []
    for appeal in result:
        appeal = dict(appeal)
        correct_appeal = await get_appeal(appeal["id"], user)
        appeals_list.append(Appeal(**dict(correct_appeal)))
    return appeals_list


async def get_appeals_page(user: UserTable) -> AppealsPage:
    appeals_list = await get_appeals(user)
    client = await get_client(user.client_id)
    software_list = await get_software_db_list()
    modules_list = await get_modules()
    return AppealsPage(**dict({"appeals": appeals_list,
                               "client": client,
                               "software_list": software_list,
                               "modules_list": modules_list}))


async def get_appeal(appeal_id: int, user: UserTable) -> Union[Appeal, DevAppeal]:
    appeal = await check_access(appeal_id, user, status.HTTP_404_NOT_FOUND)
    # TODO проверить на несуществующее поле или на None
    client = await get_client_db(appeal.client_id)
    author = await get_user(UUID4(appeal.author_id))
    responsible = None
    if appeal.responsible_id:
        responsible = await get_user(UUID4(appeal.responsible_id))
    software = await get_software(appeal.software_id)
    module = await get_module(appeal.module_id)
    comment = await get_comments(appeal_id, user)
    result = Appeal(**dict({**appeal,
                            "client": client,
                            "author": author,
                            "responsible": responsible,
                            "software": software,
                            "module": module,
                            "comments": comment}))
    if user.is_superuser:
        developers = await get_developers()
        allowed_statuses = await get_next_status(appeal_id, user)
        modules_list = await get_modules()
        software_list = await get_software_db_list()
        result = DevAppeal(**dict({**result,
                                   "software_list": software_list,
                                   "modules_list": modules_list,
                                   "developers": developers,
                                   "allowed_statuses": allowed_statuses}))
    return result


async def get_appeal_db(appeal_id: int) -> AppealDB:
    query = appeals.select().where(appeals.c.id == appeal_id)
    result = await database.fetch_one(query=query)
    if result:
        return AppealDB(**dict(result))
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def add_appeal(appeal: AppealCreate, user: UserTable) -> AppealDB:
    item = {**appeal.dict(), "client_id": int(user.client_id), "author_id": str(user.id), "status": StatusTasks.new}
    query = appeals.insert().values(item)
    appeal_id = await database.execute(query)
    await notify_create_appeal(appeal_id, user)
    return await get_appeal_db(appeal_id)


async def update_appeal(appeal_id: int, appeal: AppealUpdate, user: UserTable) -> AppealDB:
    old_appeal = await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    if old_appeal.status == StatusTasks.closed or old_appeal.status == StatusTasks.canceled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.APPEAL_IS_CLOSED)
    appeal = appeal.dict(exclude_unset=True)
    if "importance" in appeal:
        if appeal["importance"] < 0:
            appeal["importance"] = 1
        if appeal["importance"] > 5:
            appeal["importance"] = 5
    old_appeal = dict(old_appeal)
    for field in appeal:
        if appeal[field] is not None:
            old_appeal[field] = appeal[field]
    query = appeals.update().where(appeals.c.id == appeal_id).values(old_appeal)
    result_id = await database.execute(query)
    await notify_update_appeal(appeal_id, user)
    return await get_appeal_db(appeal_id)


async def update_dev_appeal(appeal_id: int, appeal: AppealUpdate, user: UserTable) -> AppealDB:
    old_appeal = await get_appeal_db(appeal_id)
    if old_appeal.status == StatusTasks.closed or old_appeal.status == StatusTasks.canceled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.APPEAL_IS_CLOSED)
    appeal = appeal.dict(exclude_unset=True)
    if "status" in appeal and (appeal["status"] == StatusTasks.closed or appeal["status"] == StatusTasks.canceled):
        appeal["date_processing"] = datetime.utcnow()
    if "responsible_id" in appeal and old_appeal.status == StatusTasks.new:
        appeal["status"] = StatusTasks.registered
    if "importance" in appeal:
        if appeal["importance"] < 0:
            appeal["importance"] = 1
        if appeal["importance"] > 5:
            appeal["importance"] = 5
    old_appeal = dict(old_appeal)
    for field in appeal:
        if appeal[field] is not None:
            old_appeal[field] = appeal[field]
    query = appeals.update().where(appeals.c.id == appeal_id).values(old_appeal)
    result_id = await database.execute(query)
    await notify_update_appeal(appeal_id, user)
    return await get_appeal_db(appeal_id)


async def delete_appeal(appeal_id: int):
    query = appeals.delete().where(appeals.c.id == appeal_id)
    result = await database.execute(query)
    return result


async def get_comments(comment_id: int, user: UserTable):
    await check_access(comment_id, user, status.HTTP_404_NOT_FOUND)
    query = comments.select().where(comments.c.appeal_id == comment_id)
    result = await database.fetch_all(query)
    return [dict(comment) for comment in result]


async def get_comment(comment_id: int, pk: int, user: UserTable):
    await check_access(comment_id, user, status.HTTP_404_NOT_FOUND)
    query = comments.select().where((comments.c.id == pk) & (comments.c.appeal_id == comment_id))
    comment = await database.fetch_one(query)
    if comment:
        comment = dict(comment)
        author = await database.fetch_one(query=users.select().where(users.c.id == comment["author_id"]))
        return {**comment, "author": author}
    return None


async def get_comment_db(comment_id: int):
    query = comments.select().where(comments.c.id == comment_id)
    result = await database.fetch_one(query=query)
    return await check_dict(result)


async def add_comment(appeal_id: int, comment: CommentCreate, user: UserTable):
    await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    item = {**comment.dict(), "appeal_id": int(appeal_id), "author_id": str(user.id)}
    query = comments.insert().values(item)
    comment_id = await database.execute(query)
    await notify_comment(appeal_id, user)
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
    if appeal.client_id != user.client_id and not user.is_superuser:
        raise HTTPException(status_code=status_code)
    return appeal


async def get_next_status(appeal_id: int, user: UserTable):
    appeal = await get_appeal_db(appeal_id)
    current_status = appeal.status
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


async def get_attachment_db(attachment_id: int) -> Optional[AttachmentDB]:
    query = attachments.select().where(attachments.c.id == attachment_id)
    result = await database.fetch_one(query=query)
    if result:
        return AttachmentDB(**dict(result))
    return None


async def get_attachment(attachment_id: int):
    attachment = await get_attachment_db(attachment_id)
    if attachment:
        return FileResponse(attachment.filename)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def add_attachment(appeal_id: int, filename: str, user_id: str) -> Optional[AttachmentDB]:
    attachment = AttachmentCreate(filename=filename,
                                  appeal_id=appeal_id,
                                  author_id=user_id,
                                  date_create=datetime.utcnow())
    query = attachments.insert().values(**dict(attachment))
    attachment_id = await database.execute(query)
    return await get_attachment_db(attachment_id)


async def upload_attachment(appeal_id: int, file: UploadFile, user: UserTable) -> Optional[AttachmentDB]:
    filename = f'{datetime.utcnow()}-{file.filename}'
    with open(f'/attachments/{filename}', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    await notify_attachment(appeal_id, user)
    return await add_attachment(appeal_id, filename, str(user.id))


async def delete_attachment(attachment_id: int) -> None:
    query = attachments.delete().where(attachments.c.id == attachment_id)
    await database.execute(query)


async def notify_create_appeal(appeal_id: int, user: UserTable) -> None:
    appeal = await get_appeal_db(appeal_id)
    client = await get_client_db(appeal.client_id)
    message = f"Представителем закачика {client.name} - {user.name} {user.surname} " \
              f"было создано обращение №{appeal_id} - {appeal.topic}"
    developers = await get_developers()
    for developer in developers:
        await notify_user(developer.email, message)
    return None


async def notify_update_appeal(appeal_id: int, user: UserTable) -> None:
    appeal = await get_appeal_db(appeal_id)
    message = f"Обращение №{appeal_id} - {appeal.topic} было измененно"
    if user.is_superuser:
        author = await get_or_404(UUID4(appeal.author_id))
        to_addr = author.email
        message += " разработчиком"
        await notify_user(to_addr, message)
    elif appeal.responsible_id:
        developer = await get_or_404(UUID4(appeal.responsible_id))
        to_addr = developer.email
        message += " представителем заказчика"
        await notify_user(to_addr, message)
    return None


async def notify_comment(appeal_id: int, user: UserTable) -> None:
    appeal = await get_appeal_db(appeal_id)
    message = f"В обращении №{appeal_id} - {appeal.topic} был оставлен комментарий"
    if user.is_superuser:
        author = await get_or_404(UUID4(appeal.author_id))
        to_addr = author.email
        await notify_user(to_addr, message)
    elif appeal.responsible_id:
        developer = await get_or_404(UUID4(appeal.responsible_id))
        to_addr = developer.email
        await notify_user(to_addr, message)
    return None


async def notify_attachment(appeal_id: int, user: UserTable) -> None:
    appeal = await get_appeal_db(appeal_id)
    message = f"В обращении №{appeal_id} - {appeal.topic} были изменены вложения"
    if user.is_superuser:
        author = await get_or_404(UUID4(appeal.author_id))
        to_addr = author.email
        await notify_user(to_addr, message)
    elif appeal.responsible_id:
        developer = await get_or_404(UUID4(appeal.responsible_id))
        to_addr = developer.email
        await notify_user(to_addr, message)
    return None


async def notify_user(to_addr: str, message: str) -> None:
    title = "Изменение обращения"
    email = Email(recipient=to_addr, title=title, message=message)
    await send_mail(email)

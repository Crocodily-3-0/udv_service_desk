import shutil
from datetime import datetime
from typing import List, Optional, Dict

from pydantic.types import UUID4

from .schemas import AppealCreate, CommentCreate, AppealUpdate, CommentUpdate, AppealList, AppealDB, Appeal, \
    DevAppeal, AppealsPage, AttachmentDB, AttachmentCreate
from ..accounts.client_account.services import get_client_db, get_client
from ..accounts.developer_account.statistics.schemas import StatusesDistribution, StatusStatistics
from ..db.db import database
from .models import appeals, comments, attachments
from ..errors import Errors
from ..reference_book.services import get_software, get_module, get_modules, get_software_db_list
from ..users.logic import get_developers, get_or_404, get_user
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
        appeals_list.append(await get_appeal_list(appeal))
    return appeals_list


async def get_appeals(user: UserTable) -> List[AppealList]:
    query = appeals.select().where(appeals.c.client_id == user.client_id)
    result = await database.fetch_all(query=query)
    appeals_list = []
    for appeal in result:
        appeal = dict(appeal)
        appeals_list.append(await get_appeal_list(appeal))
    return appeals_list


async def get_appeals_by_developer(developer_id: str) -> List[AppealDB]:
    query = appeals.select().where(appeals.c.responsible_id == developer_id)
    result = await database.fetch_all(query=query)
    return [AppealDB(**dict(appeal)) for appeal in result]


async def get_appeals_by_client(client_id: int) -> List[AppealDB]:
    query = appeals.select().where(appeals.c.client_id == client_id)
    result = await database.fetch_all(query=query)
    return [AppealDB(**dict(appeal)) for appeal in result]


async def get_appeals_by_software(software_id: int) -> List[AppealDB]:
    query = appeals.select().where(appeals.c.software_id == software_id)
    result = await database.fetch_all(query=query)
    return [AppealDB(**dict(appeal)) for appeal in result]


async def get_appeals_by_module(module_id: int) -> List[AppealDB]:
    query = appeals.select().where(appeals.c.module_id == module_id)
    result = await database.fetch_all(query=query)
    return [AppealDB(**dict(appeal)) for appeal in result]


async def get_appeals_db() -> List[AppealDB]:
    result = await database.fetch_all(appeals.select())
    return [AppealDB(**dict(appeal)) for appeal in result]


async def get_status_distribution(appeals_list: List[AppealDB]) -> StatusesDistribution:
    new = 0
    registered = 0
    in_work = 0
    closed = 0
    canceled = 0
    reopen = 0
    for appeal in appeals_list:
        if appeal.status == StatusTasks.new:
            new += 1
        elif appeal.status == StatusTasks.registered:
            registered += 1
        elif appeal.status == StatusTasks.in_work:
            in_work += 1
        elif appeal.status == StatusTasks.closed:
            closed += 1
        elif appeal.status == StatusTasks.canceled:
            canceled += 1
        elif appeal.status == StatusTasks.reopen:
            reopen += 1
    return StatusesDistribution(new=new,
                                registered=registered,
                                in_work=in_work,
                                closed=closed,
                                canceled=canceled,
                                reopen=reopen)


async def get_statuses_list(appeals_list: List[AppealDB]) -> List[StatusStatistics]:
    statuses_list = []
    statuses = {
        "new": 0,
        "registered": 0,
        "in_work": 0,
        "closed": 0,
        "canceled": 0,
        "reopen": 0,
    }
    for appeal in appeals_list:
        if appeal.status == StatusTasks.new:
            statuses["new"] += 1
        elif appeal.status == StatusTasks.registered:
            statuses["registered"] += 1
        elif appeal.status == StatusTasks.in_work:
            statuses["in_work"] += 1
        elif appeal.status == StatusTasks.closed:
            statuses["closed"] += 1
        elif appeal.status == StatusTasks.canceled:
            statuses["canceled"] += 1
        elif appeal.status == StatusTasks.reopen:
            statuses["reopen"] += 1
    for current_status in statuses:
        statuses_list.append(StatusStatistics(name=current_status, count_appeals=statuses[current_status]))
    return statuses_list


async def get_appeal_list(appeal: Dict) -> AppealList:
    author = await get_or_404(appeal["author_id"])
    client = await get_client_db(appeal["client_id"])
    responsible = await get_user(appeal["responsible_id"])
    software = await get_software(appeal["software_id"])
    module = await get_module(appeal["module_id"])
    return AppealList(**dict({
        **appeal,
        "author": author,
        "client": client,
        "responsible": responsible,
        "software": software,
        "module": module}))


async def get_appeals_page(user: UserTable) -> AppealsPage:
    appeals_list = await get_appeals(user)
    client = await get_client(user.client_id)
    software_list = await get_software_db_list()
    modules_list = await get_modules()
    return AppealsPage(**dict({"appeals": appeals_list,
                               "client": client,
                               "software_list": software_list,
                               "modules_list": modules_list}))


async def get_appeal(appeal_id: int, user: UserTable) -> Appeal:
    appeal = await check_access(appeal_id, user, status.HTTP_404_NOT_FOUND)
    client = await get_client_db(appeal.client_id)
    author = await get_user(UUID4(appeal.author_id))
    responsible = None
    if appeal.responsible_id:
        responsible = await get_user(UUID4(appeal.responsible_id))
    software = await get_software(appeal.software_id)
    module = await get_module(appeal.module_id)
    comment = await get_comments(appeal_id, user)
    result = Appeal(**dict({**dict(appeal),
                            "client": client,
                            "author": author,
                            "responsible": responsible,
                            "software": software,
                            "module": module,
                            "comments": comment}))
    return result


async def get_dev_appeal(appeal_id: int, user: UserTable, appeal: Appeal) -> DevAppeal:
    developers = await get_developers()
    allowed_statuses = await get_next_status(appeal_id, user)
    modules_list = await get_modules()
    software_list = await get_software_db_list()
    result = DevAppeal(**dict({**dict(appeal),
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
    if appeal.importance:
        if appeal.importance > 5:
            appeal.importance = 5
        elif appeal.importance < 1:
            appeal.importance = 1
    item = {**appeal.dict(), "client_id": int(user.client_id), "author_id": str(user.id), "status": StatusTasks.new}
    query = appeals.insert().values(item)
    appeal_id = await database.execute(query)
    await notify_create_appeal(appeal_id, user)
    return await get_appeal_db(appeal_id)


async def update_appeal(appeal_id: int, appeal: AppealUpdate, user: UserTable) -> AppealDB:
    old_appeal = await check_access(appeal_id, user, status.HTTP_403_FORBIDDEN)
    appeal = appeal.dict(exclude_unset=True)

    if old_appeal.status == StatusTasks.closed or old_appeal.status == StatusTasks.canceled:
        if "status" not in appeal.keys() or appeal["status"] != StatusTasks.reopen:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.APPEAL_IS_CLOSED)

    if "importance" in appeal:
        if appeal["importance"] < 1:
            appeal["importance"] = 1
        if appeal["importance"] > 5:
            appeal["importance"] = 5
    old_appeal_dict = dict(old_appeal)
    for field in appeal:
        if field not in ["status", "text"]:
            continue
        if field == "status" and (appeal[field] != StatusTasks.reopen
                                  or (old_appeal_dict["status"] != StatusTasks.canceled
                                      and old_appeal_dict["status"] != StatusTasks.closed)):
            continue
        elif appeal[field] is not None:
            old_appeal_dict[field] = appeal[field]
    if old_appeal_dict != dict(old_appeal):
        old_appeal_dict["date_edit"] = datetime.utcnow()
    query = appeals.update().where(appeals.c.id == appeal_id).values(old_appeal_dict)
    await database.execute(query)
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
        if appeal["importance"] < 1:
            appeal["importance"] = 1
        if appeal["importance"] > 5:
            appeal["importance"] = 5

    old_appeal_dict = dict(old_appeal)
    for field in appeal:
        if appeal[field] is not None:
            old_appeal_dict[field] = appeal[field]

    if old_appeal_dict != dict(old_appeal):
        old_appeal_dict["date_edit"] = datetime.utcnow()

    query = appeals.update().where(appeals.c.id == appeal_id).values(old_appeal_dict)
    await database.execute(query)
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


async def get_next_status(appeal_id: int, user: UserTable) -> List[StatusTasks]:
    appeal = await get_appeal_db(appeal_id)
    current_status = appeal.status
    if user.is_superuser:
        if current_status is StatusTasks.new:
            return [StatusTasks.registered]
        elif current_status is StatusTasks.registered:
            return [StatusTasks.in_work]
        elif current_status is StatusTasks.in_work:
            return [StatusTasks.closed, StatusTasks.canceled]
        elif current_status is StatusTasks.reopen:
            return [StatusTasks.in_work]
        else:
            return []
    elif current_status is StatusTasks.closed or current_status is StatusTasks.canceled:
        return [StatusTasks.reopen]
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
    message = f"Представителем закачика «{client.name}» - {user.name} {user.surname} " \
              f"было создано обращение №{appeal_id} - «{appeal.topic}»"
    developers = await get_developers()
    for developer in developers:
        await notify_user(developer.email, message)
    return None


async def notify_update_appeal(appeal_id: int, user: UserTable) -> None:
    appeal = await get_appeal_db(appeal_id)
    message = f"Обращение №{appeal_id} - «{appeal.topic}» было измененно"
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
    message = f"В обращении №{appeal_id} - «{appeal.topic}» был оставлен комментарий"
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
    message = f"В обращении №{appeal_id} - «{appeal.topic}» были изменены вложения"
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

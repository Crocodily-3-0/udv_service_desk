from typing import Optional, List
from datetime import datetime

from .models import StatusTasks
from pydantic import BaseModel

from ..accounts.client_account.schemas import ClientDB, Client
from ..reference_book.schemas import SoftwareDB, ModuleDB
from ..users.schemas import UserDB, DeveloperList


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentCreate):
    pass


class Comment(CommentBase):
    id: int
    appeal_id: int
    author: UserDB
    date_create: datetime


class CommentDB(CommentBase):
    id: int
    appeal_id: int
    author_id: str
    date_create: datetime


class CommentShort(CommentBase):
    id: int
    author_id: str
    date_create: datetime


class AttachmentBase(BaseModel):
    filename: str


class AttachmentCreate(AttachmentBase):
    appeal_id: int
    author_id: str
    date_create: datetime = datetime.utcnow()


class AttachmentDB(AttachmentBase):
    id: int
    appeal_id: int
    author_id: str
    date_create: datetime


class AppealBase(BaseModel):
    topic: str
    importance: int
    date_edit: Optional[datetime]


class AppealCreate(AppealBase):
    text: str
    importance: Optional[int]
    software_id: int
    module_id: int
    date_create: datetime = datetime.utcnow()
    importance: Optional[int] = 1


class AppealUpdate(AppealBase):
    topic: Optional[str]
    text: Optional[str]
    status: Optional[StatusTasks]
    software_id: Optional[int]
    module_id: Optional[int]
    responsible_id: Optional[str]
    importance: Optional[int]
    date_edit: datetime = datetime.utcnow()


class AppealShort(AppealBase):
    id: int
    text: str
    status: StatusTasks


class AppealDB(AppealBase):
    id: int
    text: str
    client_id: int
    author_id: str
    status: StatusTasks
    date_create: datetime
    date_processing: Optional[datetime]
    responsible_id: Optional[str]
    software_id: int
    module_id: int


class AppealList(AppealBase):
    id: int
    importance: int
    author: UserDB
    client: ClientDB
    date_create: datetime
    responsible: Optional[UserDB]
    status: StatusTasks
    software: SoftwareDB
    module: ModuleDB


class Appeal(AppealBase):
    id: int
    text: str
    status: StatusTasks
    date_create: datetime
    date_processing: Optional[datetime]
    client: ClientDB
    author: UserDB
    responsible: Optional[UserDB]
    software: SoftwareDB
    module: ModuleDB
    comments: Optional[List[CommentShort]]


class AppealsPage(BaseModel):
    appeals: List[AppealList]
    client: Client
    software_list: List[SoftwareDB]
    modules_list: List[ModuleDB]


class DevAppeal(Appeal):
    software_list: List[SoftwareDB]
    modules_list: List[ModuleDB]
    developers: List[DeveloperList]
    allowed_statuses: List[StatusTasks]

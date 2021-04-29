from typing import Optional, List
from datetime import datetime
from .models import StatusTasks
from pydantic import BaseModel

from ..accounts.client_account.schemas import ClientDB
from ..reference_book.schemas import SoftwareDB, ModuleShort
from ..users.schemas import UserDB


class AppealBase(BaseModel):
    topic: str
    text: str


class AppealCreate(AppealBase):
    software_id: int
    module_id: int


class AppealUpdate(AppealCreate):
    pass


class AppealShort(AppealBase):
    id: int
    status: StatusTasks


class AppealDB(AppealCreate):
    id: int
    client_id: int
    author_id: str
    status: StatusTasks
    date_create: datetime
    date_processing: Optional[datetime]
    responsible_id: Optional[int]
    software_id: int
    module_id: int


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


class Appeal(AppealBase):
    id: int
    status: StatusTasks
    date_create: datetime
    date_processing: Optional[datetime] = None
    client: ClientDB
    author: UserDB
    responsible: Optional[UserDB]
    software: SoftwareDB
    module: ModuleShort
    comment: Optional[List[CommentShort]]

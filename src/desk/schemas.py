from typing import List, Optional
from datetime import datetime
from .models import StatusTasks
from pydantic import BaseModel
from ..reference_book.schemas import SoftwareShort, ModuleShort


class AppealBase(BaseModel):
    topic: str
    text: str
    status: StatusTasks


class AppealCreate(AppealBase):
    author_id: str
    responsible_id: str
    software_id: int
    module_id: int


class AppealShort(AppealBase):
    id: int
    author: int  # TODO change to Member
    date_create: datetime
    date_processing: Optional[datetime] = None
    responsible: int  # TODO change to Developer
    software: SoftwareShort
    module: ModuleShort


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    appeal_id: int
    author_id: int


class Comment(CommentBase):
    id: int
    date_create: datetime
    appeal: AppealShort
    author: int  # TODO maybe change to member (Union[member, developer])


class CommentShort(CommentBase):
    id: int
    date_create: datetime
    author: int  # TODO maybe change to member (Union[member, developer])


class Appeal(AppealBase):
    id: int
    author: int  # TODO change to Member
    date_create: datetime
    date_processing: Optional[datetime] = None
    responsible: int  # TODO change to Developer
    software: SoftwareShort
    module: ModuleShort
    # comments: List[CommentShort] = None

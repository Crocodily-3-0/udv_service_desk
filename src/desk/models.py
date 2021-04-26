import enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, sql, Enum

from ..db.db import Base


class StatusTasks(enum.Enum):
    new = "New"
    register = "Registered"
    in_work = "In work"
    closed = "Closed"
    canceled = "Canceled"
    reopen = "Reopen"


class Appeal(Base):
    __tablename__ = 'appeal'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    topic = Column(String(100), nullable=False)
    text = Column(String(500), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'))
    author_id = Column(String, ForeignKey('user.id'))
    date_create = Column(DateTime(timezone=True), server_default=sql.func.now())
    date_processing = Column(DateTime, default=None)
    status = Column(Enum(StatusTasks), default=StatusTasks.new)
    responsible_id = Column(String, ForeignKey('user.id'), nullable=True)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('module.id'), nullable=False)
    # attachments


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    text = Column(String(300), nullable=False)
    appeal_id = Column(Integer, ForeignKey('appeal.id'), nullable=False)
    author_id = Column(String, ForeignKey('user.id'), nullable=False)
    date_create = Column(DateTime(timezone=True), server_default=sql.func.now())


appeals = Appeal.__table__
comments = Comment.__table__

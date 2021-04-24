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
    author = Column(String, ForeignKey('employee.id'))
    date_create = Column(DateTime(timezone=True), server_default=sql.func.now(), nullable=False)
    date_processing = Column(DateTime, default=None)
    status = Column(Enum(StatusTasks), default=StatusTasks.new, nullable=False)
    responsible = Column(String, ForeignKey('developer.id'), nullable=False)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('module.id'), nullable=False)
    # attachments

    # comments = relationship('Comment')


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    text = Column(String(300), nullable=False)
    appeal = Column(Integer, ForeignKey('appeal.id'), nullable=False)
    author = Column(String, ForeignKey('employee.id'), nullable=False)
    date_create = Column(DateTime(timezone=True), server_default=sql.func.now())


appeals = Appeal.__table__
comments = Comment.__table__

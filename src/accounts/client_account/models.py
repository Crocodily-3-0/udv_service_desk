from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, sql

from ...db.db import Base


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    date_create = Column(DateTime(timezone=True), server_default=sql.func.now())
    date_block = Column(DateTime, default=None, nullable=True)
    owner_id = Column(String, ForeignKey('user.id'), nullable=False)


clients = Client.__table__

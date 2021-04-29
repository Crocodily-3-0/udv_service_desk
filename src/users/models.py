from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, sql, String

from .schemas import UserDB
from ..db.db import database, Base


class UserTable(Base, SQLAlchemyBaseUserTable):
    __tablename__ = 'user'

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    # avatar
    is_owner = Column(Boolean, default=False, nullable=True)
    client_id = Column(Integer, ForeignKey('client.id'))  # TODO сделать проверку на существующего владельца клиента
    date_reg = Column(DateTime(timezone=True), server_default=sql.func.now())
    date_block = Column(DateTime, default=None, nullable=True)


users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)

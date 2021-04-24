# from tokenize import String

from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, sql, String

from .schemas import EmployeeDB, DeveloperDB
from ..db.db import database, Base


class EmployeeTable(Base, SQLAlchemyBaseUserTable):
    __tablename__ = 'employee'

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    is_owner = Column(Boolean, default=False, nullable=False)
    client = Column(Integer, ForeignKey('client.id'))
    date_reg = Column(DateTime(timezone=True), server_default=sql.func.now())
    date_block = Column(DateTime, default=None, nullable=True)
    # avatar


class DeveloperTable(Base, SQLAlchemyBaseUserTable):
    __tablename__ = 'developer'

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    # avatar


employees = EmployeeTable.__table__
employee_db = SQLAlchemyUserDatabase(EmployeeDB, database, employees)
developers = DeveloperTable.__table__
developer_db = SQLAlchemyUserDatabase(DeveloperDB, database, developers)

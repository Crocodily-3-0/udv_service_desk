from sqlalchemy import Column, DateTime, String, Integer, sql, ForeignKey, UniqueConstraint

from ..db.db import Base


class Licence(Base):
    __tablename__ = 'licence'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    number = Column(Integer, unique=True, nullable=False)
    count_members = Column(Integer, default=0, nullable=False)
    date_end = Column(DateTime(timezone=True), server_default=sql.func.now())
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)


class Module(Base):
    __tablename__ = 'module'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)  # TODO сделать проверку на ключ > 0
    UniqueConstraint(name, software_id)


class Software(Base):
    __tablename__ = 'software'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, nullable=False)  # TODO сделать проверку на непустую строку


modules = Module.__table__
licences = Licence.__table__
softwares = Software.__table__
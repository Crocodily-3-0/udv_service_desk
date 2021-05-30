from sqlalchemy import Column, DateTime, String, Integer, sql, ForeignKey, UniqueConstraint

from ..db.db import Base


class Licence(Base):
    __tablename__ = 'licence'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    number = Column(Integer, unique=True, nullable=False)
    count_members = Column(Integer, default=0, nullable=False)
    date_end = Column(DateTime(timezone=True), server_default=sql.func.now())
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)


class Module(Base):
    __tablename__ = 'module'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)  # TODO сделать проверку на ключ > 0


class Software(Base):
    __tablename__ = 'software'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, nullable=False)  # TODO сделать проверку на непустую строку


class EmployeeLicence(Base):
    __tablename__ = 'EmployeeLicence'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    employee_id = Column(String, ForeignKey('user.id'), nullable=False, unique=True)
    licence_id = Column(Integer, ForeignKey('licence.id'), nullable=False)
    UniqueConstraint(employee_id, licence_id)


class ClientLicence(Base):
    __tablename__ = 'ClientLicence'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    client_id = Column(String, ForeignKey('client.id'), nullable=False, unique=True)
    licence_id = Column(Integer, ForeignKey('licence.id'), nullable=False)
    UniqueConstraint(client_id, licence_id)


class SoftwareModules(Base):
    __tablename__ = 'SoftwareModules'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('module.id'), nullable=False)
    UniqueConstraint(software_id, module_id)


modules = Module.__table__
licences = Licence.__table__
softwares = Software.__table__
employee_licences = EmployeeLicence.__table__
software_modules = SoftwareModules.__table__
client_licences = ClientLicence.__table__
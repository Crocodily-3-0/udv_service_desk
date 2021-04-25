from datetime import datetime

import pytest

from src.db.db import database
from src.reference_book.models import softwares, licences, modules
from src.reference_book.schemas import SoftwareCreate, LicenceCreate, ModuleCreate
from src.reference_book.services import add_software, add_licence, add_module


async def clean_db(table):
    query = table.delete()
    await database.execute(query)


async def init_software():
    software = {
        "name": "Windows"
    }
    query = softwares.insert().values(software)
    await database.execute(query)


async def init_licence():
    licence = {
        "number": 555,
        "count_members": 5,
        "date_end": datetime.utcnow(),
        "client_id": 1,
        "software_id": 1
    }
    query = licences.insert().values(licence)
    await database.execute(query)


async def init_module():
    module = {
        "name": "Registration",
        "software_id": 1
    }
    query = modules.insert().values(module)
    await database.execute(query)


# @pytest.fixture()
# async def prepare_db(table, method):
#     await clean_db(table)
#     await method()
#     yield


@pytest.fixture()
async def prepare_db():
    await clean_db(softwares)
    await clean_db(licences)
    await clean_db(modules)
    await init_software()
    await init_licence()
    await init_module()
    yield


@pytest.mark.asyncio
@pytest.mark.usefixtures('prepare_db')
# @pytest.mark.usefixtures('prepare_db(softwares, init_software)')
@pytest.mark.parametrize("name", [
    "Adobe Photoshop", "Adobe Illustrator"
])
async def test_add_software(name: str):
    software = SoftwareCreate(name=name)
    result = await add_software(software)
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.usefixtures('prepare_db')
# @pytest.mark.usefixtures('prepare_db(licences, init_licence)')
@pytest.mark.parametrize(
    ("number", "count_members", "date_end", "client_id", "software_id"), [
        (-500, 5, datetime.utcnow(), 0, 1),
        (545, 5, datetime.utcnow(), 1, 10),
        (555, 5, datetime.utcnow(), -1, 10),
    ])
async def test_add_licence(
        number: int,
        count_members: int,
        date_end: datetime,
        client_id: int,
        software_id: int):
    licence = LicenceCreate(number=number,
                            count_members=count_members,
                            date_end=date_end,
                            client_id=client_id,
                            software_id=software_id)
    result = await add_licence(licence)
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.usefixtures('prepare_db')
# @pytest.mark.usefixtures('prepare_db(modules, init_module)')
@pytest.mark.parametrize(("name", "software_id"), [
    ("authorization", -1),
    ("", 10),
])
async def test_add_module(name: str, software_id: int):
    module = ModuleCreate(name=name, software_id=software_id)
    result = await add_module(module)
    assert result is not None

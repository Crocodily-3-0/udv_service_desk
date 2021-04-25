from typing import List

import pytest
from httpx import AsyncClient

from src.app import app
from src.reference_book.schemas import ModuleShort, Module, ModuleDB, \
    LicenceShort, SoftwareShort, Software, Licence, LicenceDB


@pytest.fixture(autouse=True)
async def client():
    async with AsyncClient(
            app=app,
            base_url="http://0.0.0.0/reference/") as client:
        yield client


# TODO сделать отправку данных и сравнения с моделями

@pytest.mark.asyncio
async def test_get_modules(client):
    response = await client.get("/modules/")
    assert response.status_code == 200
    assert response.json() is List[ModuleShort]


@pytest.mark.asyncio
async def test_get_module(client):
    response = await client.get("/modules/1")
    assert response.status_code == 200
    assert response.json() is Module


@pytest.mark.asyncio
async def test_post_module(client):
    response = await client.post("/modules/")
    assert response.status_code == 201
    assert response.json() is ModuleDB


@pytest.mark.asyncio
async def test_put_module(client):
    response = await client.put("/modules/1")
    assert response.status_code == 201
    assert response.json() is ModuleDB


@pytest.mark.asyncio
async def test_delete_module(client):
    response = await client.delete("/modules/1")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_licences(client):
    response = await client.get("/licences")
    assert response.status_code == 200
    assert response.json is List[LicenceShort]


@pytest.mark.asyncio
async def test_get_licence(client):
    response = await client.get("/licences/1")
    assert response.status_code == 200
    assert response.json() is Licence


@pytest.mark.asyncio
async def test_post_licence(client):
    response = await client.post("/licences/")
    assert response.status_code == 201
    assert response.json() is LicenceDB


@pytest.mark.asyncio
async def test_put_licence(client):
    response = await client.put("/licences/1")
    assert response.status_code == 201
    assert response.json() is LicenceDB


@pytest.mark.asyncio
async def test_delete_licence(client):
    response = await client.delete("/licences/1")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_softwares(client):
    response = await client.get("/software")
    assert response.status_code == 200
    assert response.json() is List[SoftwareShort]


@pytest.mark.asyncio
async def test_get_software(client):
    response = await client.get("/software/1")
    assert response.status_code == 200
    assert response.json() is SoftwareShort


@pytest.mark.asyncio
async def test_get_software_with_modules(client):
    response = await client.get("/software/1/modules")
    assert response.status_code == 200
    assert response.json() is Software


@pytest.mark.asyncio
async def test_post_software(client):
    response = await client.post("/software/")
    assert response.status_code == 201
    assert response.json() is SoftwareShort


@pytest.mark.asyncio
async def test_put_software(client):
    response = await client.put("/software/1")
    assert response.status_code == 201
    assert response.json() is SoftwareShort


@pytest.mark.asyncio
async def test_delete_software(client):
    response = await client.delete("/software/1")
    assert response.status_code == 204

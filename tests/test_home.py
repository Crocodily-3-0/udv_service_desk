import pytest
from httpx import AsyncClient

from src.app import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://0.0.0.0") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}

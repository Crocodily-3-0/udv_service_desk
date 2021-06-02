from fastapi import APIRouter, Depends, status

from src.accounts.developer_account.statistics.schemas import DevelopersStatistics, ClientsStatistics, AppealsStatistics
from src.accounts.developer_account.statistics.services import get_developers_statistics, get_clients_statistics, \
    get_appeals_statistics
from src.users.logic import developer_user
from src.users.models import UserTable


statistics_router = APIRouter()


@statistics_router.get("/appeals", response_model=AppealsStatistics, status_code=status.HTTP_200_OK)
async def developers_list(user: UserTable = Depends(developer_user)):
    return await get_appeals_statistics()


@statistics_router.get("/clients", response_model=ClientsStatistics, status_code=status.HTTP_200_OK)
async def developer(user: UserTable = Depends(developer_user)):
    return await get_clients_statistics()


@statistics_router.get("/developers", response_model=DevelopersStatistics, status_code=status.HTTP_200_OK)
async def developer(user: UserTable = Depends(developer_user)):
    return await get_developers_statistics()

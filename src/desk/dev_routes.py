from fastapi import APIRouter, status, Depends
from typing import List

from src.desk.schemas import AppealBase
from src.desk.services import get_all_appeals
from src.users.logic import developer_user
from src.users.models import UserTable

dev_router = APIRouter()


# @dev_router.get("/", response_model=List[AppealBase], status_code=status.HTTP_200_OK)
# async def all_appeals_list(user: UserTable = Depends(developer_user)):
#     return await get_all_appeals()

from fastapi import APIRouter
from .client_account.routers import client_router as client_router
from .developer_account.routers import developer_router

accounts_router = APIRouter()

accounts_router.include_router(client_router, prefix='/clients', tags=['Client'])
accounts_router.include_router(developer_router, prefix='/developers', tags=['Developer'])

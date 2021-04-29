from fastapi import FastAPI

from src.db.db import database, engine
from .db.base import Base
from .accounts.api import accounts_router
from .desk.routes import router as desk_router
from .desk.dev_routes import dev_router
from .reference_book.api.routes import router as book_router
from .users.routes import router as users_routes

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


@app.get('/', tags=['Home'])
def read_root():
    return {'Hello': 'World'}


app.include_router(accounts_router)
app.include_router(book_router, prefix='/references', tags=['Reference book'])
app.include_router(desk_router, prefix='/desk', tags=['Desk'])
app.include_router(dev_router, prefix='/desk', tags=['Desk'])
app.include_router(users_routes)

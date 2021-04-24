from fastapi import FastAPI

from src.db.db import database, engine
from .db.base import Base
from .client_account.routers import router as client_router
from .desk.routes import router as desk_router
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


@app.get('/')
def read_root():
    return {'Hello': 'World'}


app.include_router(client_router, prefix='/client', tags=['client'])
app.include_router(book_router, prefix='/reference', tags=['Reference book'])
app.include_router(desk_router, prefix='/desk', tags=['Desk'])
app.include_router(users_routes)

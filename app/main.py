from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.engine import close_db, init_db
from app.routers.alt_price import alt_price as alt_price_router
from app.routers.client import client as client_router
from app.routers.history import history as history_router
from app.routers.offering import offering as offering_router


@asynccontextmanager
async def lifespan(live_app: FastAPI):
    await init_db(live_app)

    yield

    await close_db(live_app)


app = FastAPI(lifespan=lifespan)
app.include_router(client_router)
app.include_router(offering_router)
app.include_router(alt_price_router)
app.include_router(history_router)


@app.get('/')
def main():
    return {'Hello': 'World'}


@app.get('/health')
def health():
    return {'status': 'ok'}

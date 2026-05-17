from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.engine import close_db, init_db


@asynccontextmanager
async def lifespan(live_app: FastAPI):
    await init_db(live_app)

    yield

    await close_db(live_app)


app = FastAPI(lifespan=lifespan)


@app.get('/')
def main():
    return {'Hello': 'World'}

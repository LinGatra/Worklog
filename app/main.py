import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.app_logging.logging_config import setup_logging
from app.db.engine import close_db, init_db
from app.exception_handling.http_exception_handling import AppException, app_http_exception_handler
from app.middleware.middleware_logging import LoggingMiddleware
from app.middleware.middleware_request_id import RequestIdMiddleware
from app.routers.alt_price import alt_price as alt_price_router
from app.routers.client import client as client_router
from app.routers.history import history as history_router
from app.routers.offering import offering as offering_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(live_app: FastAPI):
    await init_db(live_app)

    yield

    await close_db(live_app)


app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(client_router)
app.include_router(offering_router)
app.include_router(alt_price_router)
app.include_router(history_router)

app.add_exception_handler(AppException, app_http_exception_handler)  # type: ignore[arg-type]


@app.get('/')
def main():
    return {'Hello': 'World'}


@app.get('/health')
def health():
    return {'status': 'ok'}

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.app_logging.context import request_id_var


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        token = request_id_var.set(request_id)

        try:
            response = await call_next(request)
            response.headers['X-Request-ID'] = request_id
            return response
        finally:
            request_id_var.reset(token)

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        logger.info(
            'request_started',
            extra={
                'method': request.method,
                'path': request.url.path,
            },
        )

        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            logger.exception(
                'request_failed',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                'request_finished',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': status_code,
                    'duration_ms': duration_ms,
                },
            )

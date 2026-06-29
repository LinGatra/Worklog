import logging

from app.app_logging.context import request_id_var


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class SuppressAsgiExceptionFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage() != 'Exception in ASGI application\n'

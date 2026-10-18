import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'app.app_logging.logging_filters.RequestIdFilter',
        },
        'supress_asgi_exception': {
            '()': 'app.app_logging.logging_filters.SuppressAsgiExceptionFilter',
        },
    },
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.json.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'filters': ['request_id'],
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'uvicorn.access': {'level': 'WARNING'},
        'uvicorn.error': {
            'handlers': ['console'],
            'filters': ['supress_asgi_exception'],
            'propagate': False,
        },
        'sqlalchemy.engine': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': False,
        },
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

import functools
import logging
from _collections_abc import Callable, Coroutine
from typing import Any, TypeVar

from app.exception_handling.domain_exceptions import (
    ForeignKeyViolation,
    NotFound,
    UniqueConstraintViolation,
)

logger = logging.getLogger('business_events')

T = TypeVar('T')


def log_business_event(action: str) -> Callable:
    """
    Декоратор для методов BaseService.
    Логирует: модель, действие, результат (успех/ошибка).
    Предполагает, что у self есть self.repo.model (или похожее) для имени модели.
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            model_name = self.repo.model.__name__

            try:
                result = await func(self, *args, **kwargs)

            except NotFound as e:
                logger.warning(
                    'business_event_failed',
                    extra={
                        'model': model_name,
                        'action': action,
                        'status': 'error',
                        'error_type': type(e).__name__,
                    },
                )
                raise

            except ForeignKeyViolation as e:
                logger.warning(
                    'business_event_failed',
                    extra={
                        'model': model_name,
                        'action': action,
                        'status': 'error',
                        'error_type': type(e).__name__,
                    },
                )
                raise

            except UniqueConstraintViolation as e:
                logger.warning(
                    'business_event_failed',
                    extra={
                        'model': model_name,
                        'action': action,
                        'status': 'error',
                        'error_type': type(e).__name__,
                    },
                )
                raise

            except Exception as e:
                logger.warning(
                    'business_event_failed',
                    extra={
                        'model': model_name,
                        'action': action,
                        'status': 'error',
                        'error_type': type(e).__name__,
                    },
                )
                raise
            else:
                logger.info(
                    'business_event_succeeded',
                    extra={
                        'model': model_name,
                        'action': action,
                        'status': 'success',
                    },
                )
                return result

        return wrapper

    return decorator

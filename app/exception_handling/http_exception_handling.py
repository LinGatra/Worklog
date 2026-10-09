from fastapi import Request
from fastapi.responses import JSONResponse

from app.exception_handling.domain_exceptions import (
    CheckConstraintViolation,
    DomainValidationException,
    ForeignKeyViolation,
    NotFound,
    NotNullViolation,
    UniqueConstraintViolation,
)


async def not_found_handler(request: Request, exc: NotFound):
    return JSONResponse(status_code=404, content={'error': {'code': 404, 'message': 'Not found'}})


async def bad_request_handler(request: Request, exc: ForeignKeyViolation):
    return JSONResponse(status_code=400, content={'error': {'code': 400, 'message': 'Bad request'}})


async def unique_violation_handler(request: Request, exc: UniqueConstraintViolation):
    return JSONResponse(
        status_code=409, content={'error': {'code': 409, 'message': 'Object conflict'}}
    )


async def not_null_handler(request: Request, exc: NotNullViolation):
    return JSONResponse(
        status_code=422,
        content={'error': {'code': 422, 'message': 'One of the key fields is passed as null'}},
    )


async def check_constraint_violation_handler(request: Request, exc: CheckConstraintViolation):
    return JSONResponse(
        status_code=400,
        content={
            'error': {'code': 400, 'message': 'One of the restrictions was unexpectedly violated'}
        },
    )


async def domain_validation_handler(request: Request, exc: DomainValidationException):
    return JSONResponse(
        status_code=422,
        content={'error': {'code': 422, 'message': 'The entered data has not been validated.'}},
    )

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str | None = None, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = 'Unauthorized'):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = 'Forbidden'):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = 'Not found'):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = 'Bad request'):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class ConflictException(AppException):
    def __init__(self, detail: str = 'Object conflict'):
        super().__init__(status.HTTP_409_CONFLICT, detail)


class ServiceUnavailableException(AppException):
    def __init__(self, detail: str = 'Service unavailable'):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail)


async def app_http_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': {
                'code': exc.status_code,
                'message': exc.detail,
            },
        },
    )

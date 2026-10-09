from sqlalchemy.exc import IntegrityError

from app.exception_handling.domain_exceptions import (
    CheckConstraintViolation,
    ForeignKeyViolation,
    NotNullViolation,
    UniqueConstraintViolation,
)


def map_integrity_error(e: IntegrityError) -> Exception:
    sqlstate = getattr(e.orig, 'sqlstate', None)
    match sqlstate:
        case '23514':
            return CheckConstraintViolation()
        case '23502':
            return NotNullViolation()
        case '23505':
            return UniqueConstraintViolation()
        case '23503':
            return ForeignKeyViolation()
        case _:
            return e

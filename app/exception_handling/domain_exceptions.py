class ForeignKeyViolation(Exception):
    pass


class UniqueConstraintViolation(Exception):
    pass


class NotFound(Exception):
    pass


class NotNullViolation(Exception):
    pass


class CheckConstraintViolation(Exception):
    pass


class DomainValidationException(Exception):
    pass

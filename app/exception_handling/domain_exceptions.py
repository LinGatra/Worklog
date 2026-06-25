class ForeignKeyViolation(Exception):
    pass


class UniqueConstraintViolation(Exception):
    pass


class NotFound(Exception):
    pass

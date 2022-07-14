class FiasException(Exception):
    code: int


class FiasNotFoundException(FiasException):
    code = 404

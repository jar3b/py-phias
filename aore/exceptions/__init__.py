class FiasException(Exception):
    code: int


class FiasNotFoundException(FiasException):
    code = 404


class FiasBadDataException(FiasException):
    code = 400

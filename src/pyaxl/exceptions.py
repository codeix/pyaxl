class PyAXLException(Exception):
    pass


class UpdateException(PyAXLException):
    pass


class CreationException(PyAXLException):
    pass


class RemoveException(PyAXLException):
    pass


class ReloadException(PyAXLException):
    pass


class LogoutException(PyAXLException):
    pass


class NotAttachedException(PyAXLException):
    pass

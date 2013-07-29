__all__ = ["Error", "AbsPathError", "NotFoundError",
           "NotFoundExtsError", "UndeclaredExtError",
           "CircularIncludeError", "UnknownFormatterError",
           "ValidatorConvertError", "ValidatorCheckError"]

class Error(Exception):
    pass


class AbsPathError(Error):
    pass


class NotFoundError(Error):
    pass


class NotFoundExtsError(Error):
    pass


class UndeclaredExtError(Error):
    pass


class FileHandleError(Error):
    pass


class CircularIncludeError(FileHandleError):
    pass


class UnknownFormatterError(Error):
    pass


class ValidatorConvertError(Error):
    pass


class ValidatorCheckError(Error):
    pass


class ValidatorNodeError(Error):
    pass



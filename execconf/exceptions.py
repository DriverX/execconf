__all__ = ["AbsPathError", "NotFoundError", "NotFoundExtsError",
           "UndeclaredExtError", "CircularIncludeError",
           "ValidatorConvertError", "ValidatorCheckError"]


class AbsPathError(IOError):
    pass


class NotFoundError(IOError):
    pass


class NotFoundExtsError(IOError):
    pass


class UndeclaredExtError(ValueError):
    pass


class CircularIncludeError(RuntimeError):
    pass


class ValidatorConvertError(Exception):
    pass


class ValidatorCheckError(Exception):
    pass


class ValidatorNodeError(Exception):
    pass







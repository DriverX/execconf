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


class ValidatorConvertError(ValueError):
    pass


class ValidatorCheckError(ValueError):
    pass



from nodes import Node

__all__ = ["Validator"]

class Validator(object):
    def __init__(self, AVT, only_declared=False):
        if not isinstance(AVT, Node):
            raise TypeError("AVT must be %s instance, not %s" % (Node.__name__, type(AVT)))

        # Abstract Validation Tree
        self._AVT = AVT

        # TODO
        self._only_decl = only_declared

    def cleanup(self):
        pass

    def validate(self, data):
        return self._AVT.check(data)




from os import path
from copy import deepcopy
from utils import deep_merge

__all__ = ["DummyHelper", "IncludeHelper", "MergeHelper",
           "MergeOptionHelper"]

class BaseHelper(object):
    NAME = None
    
    def __hash__(self):
        return hash(("helper", self.NAME))

    def caller(self, loader, *args, **kwargs):
        pass

    def merge(self, left, right, *args, **kwargs):
        return


class DummyHelper(BaseHelper):
    NAME = "dummy"
    
    def merge(self, left, right, *args, **kwargs):
        data = deepcopy(left)
        if right:
            data.update(deepcopy(right))
        return data


class IncludeHelper(DummyHelper):
    NAME = "include"
    
    def caller(self, loader, filepath):
        filepath = loader.parent_join(filepath)
        loader.handle(filepath, helper=self)


class MergeHelper(BaseHelper):
    NAME = "merge"
    
    def caller(self, loader, filepath):
        loader.handle(filepath, helper=self)

    def merge(self, left, right):
        return deep_merge(left, right)


class MergeOptionHelper(BaseHelper):
    NAME = "merge_option"
    
    def caller(self, loader, filepath, *args, **kwargs):
        loader.handle(filepath, helper=self,
                helper_args=args, helper_kwargs=kwargs)

    def merge(self, left, right, options, depth=-1):
        if not isinstance(options, (list, tuple)):
            options = set([options])
        else:
            options = set(options)

        result = deepcopy(left)
        for o in options:
            if o in right:
                if depth == 0:
                    result[o] = deepcopy(right[o])
                else:
                    depth -= 1
                    result[o] = deep_merge(result.get(o), right[o], depth=depth)
        return result 




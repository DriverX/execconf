from os import path

__all__ = []

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
        data = left
        if right:
            data = left.copy()
            data.update(right)
        return data


class IncludeHelper(DummyHelper):
    NAME = "include"
    
    def caller(self, loader, filepath):
        # print "=== PARENT FILEPATH ==="
        # print hash(self), loader.parent_filepath
        # print "======================="

        filepath = loader.parent_join(filepath)
        loader.handle(filepath, helper=self)


class MergeHelper(BaseHelper):
    NAME = "merge"
    
    def caller(self, loader, filepath):
        loader.handle(filepath, helper=self)

    def merge(self, left, right):
        return left


class MergeOptionHelper(BaseHelper):
    NAME = "merge_option"
    
    def caller(self, loader, filepath, options, deep=-1):
        loader.handle(filepath, helper=self,
                helper_args=[options], helper_kwargs={"deep": deep})

    def merge(self, left, right, options, deep=-1):
        return left




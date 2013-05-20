import copy

__all__ = ["frozendict", "make_hashable", "deep_merge"]

def make_hashable(obj):
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(sub) for sub in obj)
    if isinstance(obj, set):
        return frozenset(obj)
    if isinstance(obj, dict):
        return tuple(make_hashable(i) for i in obj.iteritems())
    return obj

class frozendict(dict):
    def _blocked_attribute(obj):
        raise AttributeError, "A frozendict cannot be modified."
    _blocked_attribute = property(_blocked_attribute)

    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute

    def __new__(cls, *args, **kw):
        new = dict.__new__(cls)

        args_ = []
        for arg in args:
            if isinstance(arg, dict):
                arg = copy.copy(arg)
                for k, v in arg.items():
                    if isinstance(v, dict):
                        arg[k] = frozendict(v)
                    elif isinstance(v, list):
                        v_ = list()
                        for elm in v:
                            if isinstance(elm, dict):
                                v_.append( frozendict(elm) )
                            else:
                                v_.append( elm )
                        arg[k] = tuple(v_)
                args_.append( arg )
            else:
                args_.append( arg )

        dict.__init__(new, *args_, **kw)
        return new

    def __init__(self, *args, **kw):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            h = self._cached_hash = hash(make_hashable(self))
            return h

    def __repr__(self):
        return "frozendict(%s)" % dict.__repr__(self)

def deep_merge(dleft, dright, depth=-1, _clvl=0):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.
    
    from http://www.xormedia.com/recursively-merge-dictionaries-in-python/'''

    if not isinstance(dright, dict) or not isinstance(dleft, dict):
        return copy.deepcopy(dright)
    result = copy.deepcopy(dleft)
    for k, v in dright.iteritems():
        if _clvl != depth and k in result and isinstance(result[k], dict):
            _clvl += 1
            result[k] = deep_merge(result[k], v, depth=depth, _clvl=_clvl)
        else:
            result[k] = copy.deepcopy(v)
    return result



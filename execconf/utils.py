import copy

__all__ = ["frozendict", "make_hashable", "deep_merge",
           "recursive_fmt", "to_primitive"]

def make_hashable(obj):
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(sub) for sub in obj)
    if isinstance(obj, set):
        return frozenset(obj)
    if isinstance(obj, dict):
        return tuple(make_hashable(i) for i in obj.iteritems())
    return obj

class frozendict(dict):
    def _blocked_attribute(self, *args, **kwargs):
        raise AttributeError("A %s cannot be modified." % self.__class__.__name__)
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
                        arg[k] = cls(v)
                    elif isinstance(v, list):
                        v_ = list()
                        for elm in v:
                            if isinstance(elm, dict):
                                v_.append(cls(elm))
                            else:
                                v_.append(elm)
                        arg[k] = tuple(v_)
                args_.append(arg)
            else:
                args_.append(arg)

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
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

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

def recursive_fmt(obj, repl):
    if isinstance(obj, dict):
        return dict((recursive_fmt(k, repl), recursive_fmt(v, repl)) for (k, v) in obj.iteritems())
    elif isinstance(obj, list):
        return list(recursive_fmt(i, repl) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_fmt(i, repl) for i in obj)
    elif isinstance(obj, basestring):
        return obj % repl
    else:
        return obj 

def to_primitive(obj):
    if isinstance(obj, dict):
        return dict((to_primitive(k), to_primitive(v)) for (k, v) in obj.iteritems())
    elif isinstance(obj, list):
        return list(to_primitive(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(to_primitive(i) for i in obj)
    elif isinstance(obj, str):
        return str(obj)
    elif isinstance(obj, unicode):
        return unicode(obj)
    else:
        return obj


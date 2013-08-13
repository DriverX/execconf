from ..exceptions import ValidatorConvertError, ValidatorCheckError, \
                         ValidatorNodeError

__all__ = ["Node", "DeclNode", "Boolean", "Integer", "Float", "String",
           "List", "ListBoolean", "ListInteger", "ListFloat", "ListString",
           "ListDict", "Dict", "Option", "Pass", "LOADER_GLOBALS"]

_ConvertErrorDummyMsg = "%s: value '%s' can't convert: %s"

class Node(object):
    def check(self, value):
        return value


class DeclNode(Node):
    def __init__(self, decl):
        self._decl = decl


class Pass(Node):
    pass


class Boolean(Node):
    def __init__(self, eq=None):
        self._eq = eq

    def check(self, value):
        orig_value = value
        if not isinstance(orig_value, bool):
            if isinstance(orig_value, basestring):
                value = orig_value.lower()
            if value in ("true", "on", "yes", 1):
                value = True
            elif value in ("false", "off", "no", 0):
                value = False
            else:
                raise ValidatorConvertError(_ConvertErrorDummyMsg % ("Boolean", orig_value, type(orig_value)))

        eq = self._eq
        if eq is not None:
            if eq != value:
                raise ValidatorCheckError("value %s not equal %s" % (orig_value, eq))
        return value


class String(Node):
    def __init__(self, eq=None, min=None, max=None):
        assert min is None or min >= 0
        assert max is None or max >= 1
        if min is not None and max is not None:
            assert min <= max
        
        self._eq = eq
        self._minlen = min
        self._maxlen = max

    def check(self, value):
        orig_value = value
        if isinstance(value, basestring):
            try:
                value = unicode(value)
            except UnicodeError, e:
                raise ValidatorConvertError(_ConvertErrorDummyMsg % ("String", orig_value ,e))
        else:
            raise ValidatorConvertError(_ConvertErrorDummyMsg % ("String", orig_value, type(orig_value)))

        eq = self._eq
        minlen = self._minlen
        maxlen = self._maxlen
        vallen = len(value)
        except_ranges = "minlen=%s, maxlen=%s, len=%i" % (minlen, maxlen, vallen)

        if eq is not None:
            if eq != value:
                raise ValidatorCheckError("value '%s' not equal '%s'" % (orig_value, eq))

        if minlen is not None:
            if vallen < minlen:
                raise ValidatorCheckError("value '%s' too short. %s" % (orig_value, except_ranges))
        if maxlen is not None:
            if vallen > maxlen:
                raise ValidatorCheckError("value '%s' too long. %s" % (orig_value, except_ranges))

        return value


class Integer(Node):
    def __init__(self,
            eq=None,
            lt=None, gt=None,
            lte=None, gte=None,
            min=None, max=None):
        if eq is not None:
            assert lt is None
            assert gt is None
            assert lte is None
            assert gte is None
        if lt is not None or gt is not None:
            assert eq is None
            if lt is not None:
                assert lte is None
            if gt is not None:
                assert gte is None
        if lte is not None or gte is not None:
            assert eq is None
            if lte is not None:
                assert lt is None
            if gte is not None:
                assert gt is None
        if min is not None and max is not None:
            assert min <= max

        self._eq = eq
        self._lt = lt
        self._gt = gt
        self._lte = lte
        self._gte = gte
        self._min = min
        self._max = max

    def convert(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidatorConvertError(_ConvertErrorDummyMsg % ("Integer", value, type(value)))
    
    def check(self, value):
        orig_value = value
        value = self.convert(value)

        eq = self._eq
        lt = self._lt
        gt = self._gt
        lte = self._lte
        gte = self._gte
        mmin = self._min
        mmax = self._max
        if eq is not None:
            if value != eq:
                raise ValidatorCheckError("value %s not equal %s" % (orig_value, eq))
        if lt is not None:
            if value >= lt:
                raise ValidatorCheckError("value %s not less than %s" % (orig_value, lt))
        if lte is not None:
            if value > lte:
                raise ValidatorCheckError("value %s not less and not equal than %s" % (orig_value, lte))
        if gt is not None:
            if value <= gt:
                raise ValidatorCheckError("value %s not greater than %s" % (orig_value, gt))
        if gte is not None:
            if value < gte:
                raise ValidatorCheckError("value %s not greater and not equal than %s" % (orig_value, gte))
        if mmin is not None:
            if value < mmin:
                raise ValidatorCheckError("value %s less than %s" % (orig_value, mmin))
        if mmax is not None:
            if value > mmax:
                raise ValidatorCheckError("value %s greater than %s" % (orig_value, mmax))

        return value


class Float(Integer):
    def __init__(self, eq=None, precision=None, **kwargs):
        super(Float, self).__init__(eq=eq, **kwargs)

        if precision is not None:
            assert precision >= 0
        self._precision = precision

    def convert(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidatorConvertError(_ConvertErrorDummyMsg % ("Float", value,type(value)))

    def check(self, value):
        orig_value = value
        value = super(Float, self).check(orig_value)

        precision = self._precision
        if precision is not None:
            powed_ten = pow(10, precision)
            value = float(int(value * powed_ten))/powed_ten
        return value


class Option(Node):
    def __init__(self, *options):
        self._options = options

    def check(self, value):
        found = None
        for o in self._options:
            if isinstance(o, Node):
                try:
                    found = o.check(value)
                    break
                except:
                    pass
            elif value == o:
                found = o
                break
        
        if found is None:
            raise ValidatorCheckError("value %s not contains in options" % (value))
        return found


class List(DeclNode):
    def __init__(self, decl=None, force=False, min=None, max=None, loop=True):
        super(List, self).__init__(decl)
        
        assert min is None or min >= 0
        assert max is None or max >= 1
        if min is not None and max is not None:
            assert min <= max
        
        if self._decl is not None:
            assert isinstance(self._decl, list)
            assert len(self._decl) >= 1

        self._force = force
        self._min = min
        self._max = max
        self._loop = loop
    
    def _check_decl(self, value):
        new_value = []
        node = None
        iterdecl = iter(self._decl)
        for item in value:
            try:
                node = iterdecl.next()
            except StopIteration:
                if self._loop:
                    iterdecl = iter(self._decl)
                    node = iterdecl.next()
                else:
                    node = None
                    
            if node is None:
                raise ValidatorCheckError("list size %s greater than declared checks %s" % (len(value), len(self._decl)))
            new_item = node.check(item)
            new_value.append(new_item)
        return new_value

    def check(self, value):
        orig_value = value
        if not isinstance(orig_value, (tuple, list)):
            if self._force:
                value = [orig_value]
            else:
                raise ValidatorConvertError(_ConvertErrorDummyMsg % ("List", value, type(orig_value)))
        else:
            value = list(orig_value)

        mmin = self._min
        mmax = self._max
        vlen = len(value)
        if mmin is not None:
            if vlen < mmin:
                raise ValidatorCheckError("list size %i less than %i" % (vlen, mmin))
        if mmax is not None:
            if vlen > mmax:
                raise ValidatorCheckError("list size %i greater than %i" % (vlen, mmax))
        
        if self._decl is not None:
            value = self._check_decl(value)

        return value


class ListBoolean(List):
    def __init__(self, **kwargs):
        super(ListBoolean, self).__init__([Boolean()], loop=True, **kwargs)


class ListInteger(List):
    def __init__(self, **kwargs):
        super(ListInteger, self).__init__([Integer()], loop=True, **kwargs)


class ListFloat(List):
    def __init__(self, **kwargs):
        super(ListFloat, self).__init__([Float()], loop=True, **kwargs)


class ListString(List):
    def __init__(self, **kwargs):
        super(ListString, self).__init__([String()], loop=True, **kwargs)


class ListDict(List):
    def __init__(self, **kwargs):
        super(ListDict, self).__init__([Dict()], loop=True, **kwargs)


class Dict(DeclNode):
    def __init__(self, decl=None, min=None, max=None, required=None):
        super(Dict, self).__init__(decl)
        
        assert min is None or min >= 0
        assert max is None or max >= 1
        if min is not None and max is not None:
            assert min <= max

        if self._decl is not None and not isinstance(self._decl, dict):
            raise TypeError("decl must be dict, not %s" % type(self._decl))

        self._min = min
        self._max = max
        self._required = required
       

        self._decl_prim_keys = {}
        self._decl_node_key = None
        
        decl = self._decl
        if decl is not None:
            for k, v in decl.iteritems():
                if isinstance(k, Node):
                    if self._decl_node_key is not None:
                        raise ValidatorNodeError("dict validation node key must declared once")

                    accepted_types = (Pass, Boolean, Integer, Float, String, Option)
                    if isinstance(k, accepted_types):
                        self._decl_node_key = (k, v)
                    else:
                        raise ValidatorNodeError("dict validation node key must be one of following types: %s. %s" % (", ".join(map(str, accepted_types)), type(k)))
                else:
                    self._decl_prim_keys[k] = v

    def check(self, value):
        orig_value = value
        if not isinstance(orig_value, dict):
            raise ValidatorConvertError(_ConvertErrorDummyMsg % ("Dict", orig_value, type(orig_value)))
        
        mmin = self._min
        mmax = self._max
        vlen = len(orig_value)
        if mmin is not None:
            if vlen < mmin:
                raise ValidatorCheckError("dict size %i less than %i" % (vlen, mmin))
        if mmax is not None:
            if vlen > mmax:
                raise ValidatorCheckError("dict size %i greater than %i" % (vlen, mmax))
        
        if self._decl is None:
            value = orig_value.copy()
        else:
            # create new dict
            value = {}
            
            decl_node_key = self._decl_node_key
            for k, v in orig_value.iteritems():
                if k in self._decl_prim_keys:
                    value[k] = self._decl_prim_keys[k].check(v)
                elif decl_node_key is not None:
                    value[decl_node_key[0].check(k)] = decl_node_key[1].check(v)
                else:
                    value[k] = v

        if self._required:
            for item_name in self._required:
                if item_name not in value:
                    raise ValidatorCheckError("required item '%s' not found" % item_name)

        return value


LOADER_GLOBALS = {
    "Boolean": Boolean,
    "Integer": Integer,
    "Float": Float,
    "String": String,
    "List": List,
    "ListBoolean": ListBoolean,
    "ListInteger": ListInteger,
    "ListFloat": ListFloat,
    "ListString": ListString,
    "ListDict": ListDict,
    "Dict": Dict,
    "Option": Option,
    "Pass": Pass
}

CLI_TYPES = {"pass": Pass(),
             "str": String(),
             "bool": Boolean(),
             "int": Integer(),
             "float": Float()}



from __future__ import absolute_import
# json imports
try:
    import simplejson as json
except ImportError:
    import json

# pickle imports
try:
    import cPickle as pickle
except ImportError:
    import pickle

# yaml imports
yaml = None
try:
    import yaml
except ImportError:
    pass

__all__ = ["has_yaml", "JSONFormatter", "YAMLFormatter", "PickleFormatter"]

def has_yaml():
    return bool(yaml)

class BaseFormatter(object):
    def format(self, data):
        raise NotImplementedError()


class JSONFormatter(BaseFormatter):
    def __init__(self, pretty_print=True):
        self.indent = None
        self.sort_keys = False
        if pretty_print:
            self.indent = 4
            self.sort_keys = True

    def format(self, data):
        ret = json.dumps(data, 
                         indent=self.indent,
                         sort_keys=self.sort_keys)
        return ret


class YAMLFormatter(BaseFormatter):
    def __init__(self, canonical=False):
        self.canonical = canonical

    def format(self, data):
        if not has_yaml():
            raise NotImplementedError("yaml module is not installed")
        return yaml.safe_dump(data, canonical=self.canonical)


class PickleFormatter(BaseFormatter):
    def format(self, data):
        return pickle.dumps(data)


type2cls = {"yaml": YAMLFormatter,
            "json": JSONFormatter,
            "pickle": PickleFormatter}


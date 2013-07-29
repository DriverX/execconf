from __future__ import absolute_import
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json
try:
    import cPickle as pickle
except ImportError:
    import pickle

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
        return


class JSONFormatter(BaseFormatter):
    def format(self, data):
        return json.dumps(data)


class YAMLFormatter(BaseFormatter):
    def format(self, data):
        if yaml is None:
            raise NotImplementedError("yaml module is not installed")
        return yaml.dump(data)


class PickleFormatter(BaseFormatter):
    def format(self, data):
        return pickle.dumps(data)



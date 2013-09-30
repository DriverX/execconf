from __future__ import absolute_import
try:
    import simplejson as json
except ImportError:
    import json
try:
    import yaml
except ImportError:
    yaml = None
from .utils import frozendict, to_primitive

__all__ = ["Config"]

class Config(frozendict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        
        self.__dict__.update(self)

    def __setattr__(self, k, v):
        raise AttributeError("Config cannot be modified.")

    def __delattr__(self, k):
        raise AttributeError("Config cannot be modified.")
    
    def _to_dict(self):
        return to_primitive(self)

    def _to_json(self, pretty_print=True):
        kw = {}
        if pretty_print:
            kw["indent"] = 4
            kw["sort_keys"] = True
        return json.dumps(self.__dict__, **kw)

    def _to_yaml(self, canonical=False):
        if not yaml:
            raise NotImplementedError("yaml module is not installed")
        return yaml.safe_dump(self._to_dict(), canonical=canonical)



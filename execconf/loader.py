from os import path
from types import ModuleType
import runpy
from config import Config
from validator import Validator
from validator.nodes import Node, Dict, LOADER_GLOBALS
from builder import Builder
from exceptions import AbsPathError, NotFoundError, \
                       NotFoundExtsError, UndeclaredExtError, \
                       CircularIncludeError


__all__ = ["Loader", "ConfigLoader", "ValidatorLoader"]


class Loader(object):
    defaults_exts = ("py",)

    def __init__(self, directory, exts=None, defaults=None):
        self._directory = path.abspath(directory)

        if exts is not None:
            if isinstance(exts, basestring):
                exts = (exts,)
            else:
                exts = tuple(exts)
        else:
            exts = self.defaults_exts
        self._exts = exts

        self._defaults = defaults
        self._data = {}
    
    def cleanup(self):
        self._data = {}

    def joinpath(self, *args):
        return path.join(self._directory, *args)

    def _resolve_filepath(self, filepath):
        ret = None
        filepath = path.normpath(filepath)
        if path.isabs(filepath):
            drive, tail = path.splitdrive(filepath)
            if drive:
                raise AbsPathError("absolute path with drive not allowed: %s" % filepath)
            filepath = filepath[1:]
        filename, ext = path.splitext(filepath)
        if not ext:
            found_filepath = None
            for ext in self._exts:
                ext = "." + ext
                check_filepath = filepath + ext
                if path.exists(self.joinpath(check_filepath)):
                    found_filepath = check_filepath
                    break
            if found_filepath is None:
                raise NotFoundExtsError("file %s not found with any declared extensions: %s" % (filepath, ", ".join(self._exts)))
            filepath = found_filepath
        elif ext[1:] not in self._exts:
            raise UndeclaredExtError("file %s has undeclared extension %s" % (filepath, ext))
        else:
            if not path.exists(self.joinpath(filepath)):
                raise NotFoundError("file %s not found in %s" % (filepath, self._directory))
        
        ret = filepath
        return ret
    
    def _filter_data(self, data):
        ret = {}
        approve_types = (
                bool, int, float, long,
                basestring, list, tuple,
                set, frozenset, dict, type(None), Node)
        for k, v in data.iteritems():
            if (k.startswith("_") or
                    callable(v) or
                    isinstance(v, ModuleType)):
                continue
            if isinstance(v, approve_types):
                ret[k] = v
        return ret

    def _run_path(self, filepath, init_globals=None):
        fullpath = self.joinpath(filepath)
        data = runpy.run_path(fullpath, init_globals)
        data = self._filter_data(data)
        return data
    
    def _load_defaults(self):
        defaults = self._defaults
        data = None
        if defaults is not None:
            if isinstance(defaults, basestring):
                defaults_filepath = self._resolve_filepath(defaults)
                data = self._run_path(defaults_filepath)
            elif isinstance(defaults, ModuleType):
                data = self._filter_data(vars(defaults))
            elif isinstance(defaults, dict):
                data = self._filter_data(defaults)

            if data is not None:
                self._extend_data(data)
            else:
                raise TypeError("defaults options must be string of path to file or dict or some package: %s", type(defaults))

    def _load(self, filepath, extra=None):
        self._load_defaults()

        filepath = self._resolve_filepath(filepath)
        data = self._run_path(filepath)
        self._extend_data(data)
        
        if extra is not None:
            self._extend_data(data, extra)

        return self._data
    
    def _extend_data(self, extra_data):
        self._data.update(extra_data)
        return self._data

    def load(self, filepath, extra=None):
        self.cleanup()

        data = self._load(filepath, extra=extra)
        conf = self.convert(data)
        return conf

    def convert(self, data):
        return data


class ConfigLoader(Loader):
    def __init__(self, directory,
            exts=None,
            builder=None,
            validator=None,
            **kwargs):
        super(ConfigLoader, self).__init__(directory, exts=exts, **kwargs)

        if validator is not None and not isinstance(validator, Validator):
            raise TypeError("option validator must be istance of Validator")
        if builder is not None and not isinstance(builder, Builder):
            raise TypeError("option builder must be istance of Builder")
        self._validator = validator
        self._builder = builder

        self._files_data = {}
        self._files_queue = []
    
    def cleanup(self):
        super(ConfigLoader, self).cleanup()

        self._files_data = {}
        self._files_queue = []

        if self._validator:
            self._validator.cleanup()
        if self._builder:
            self._builder.cleanup()

    def _get_include_def(self, root_filepath, included):
        root_dirname = path.dirname(root_filepath)

        def include(filepath):
            filepath = self._resolve_filepath(path.join(root_dirname, filepath))
            self._handle(filepath, _included=included)

        return include

    def _handle(self, filepath, _included=None):
        if _included is None:
            _included = []
        if filepath in _included:
            raise CircularIncludeError("%s already included: %s" % (filepath, "->".join(_included)))
        
        self._files_queue.append(filepath)

        if filepath not in self._files_data:
            # append filepath for check cycling include
            _included.append(filepath)

            include_def = self._get_include_def(filepath, _included)
            data = self._run_path(filepath, {"include": include_def})
            
            # remove filepath
            _included.remove(filepath)
            
            # add data
            self._files_data[filepath] = data
    
    def _collect_result_data(self):
        for f in self._files_queue:
            data = self._files_data[f]
            if data:
                self._extend_data(data)
    
    def _load(self, filepath, extra=None):
        self._load_defaults()

        validator = self._validator
        builder = self._builder
         
        filepath = self._resolve_filepath(filepath)
        self._handle(filepath)
        
        self._collect_result_data()
        
        if extra is not None:
            self._extend_data(extra)

        data = self._data
        if builder:
            data = builder.build(data)
        
        if validator:
            data = validator.validate(data)

        self._data = data
        return data

    def convert(self, data):
        return Config(data)


class ValidatorLoader(Loader):
    def _load(self, filepath, extra=None):
        filepath = self._resolve_filepath(filepath)
        data = self._run_path(filepath, LOADER_GLOBALS)
        self._extend_data(data)

        if extra is not None:
            self._extend_data(extra)
        return self._data

    def convert(self, data):
        AVT = None
        validation = data.get("EXEC_VALIDATION")
        
        # TODO
        only_declared = data.get("EXEC_ONLY_DECLARED", False)
        if validation is not None:
            if isinstance(validation, Dict):
                AVT = validation
            else:
                AVT = Dict(validation)
        else:
            AVT = Dict(data)

        validator = Validator(AVT, only_declared=only_declared)
        return validator



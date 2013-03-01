from os import path
from types import ModuleType
import runpy
from config import Config
from validator import Validator
from validator.nodes import Dict, LOADER_GLOBALS
from builder import Builder
from exceptions import AbsPathError, NotFoundError, \
                       NotFoundExtsError, UndeclaredExtError, \
                       CircularIncludeError


__all__ = ["Loader", "ConfigLoader", "ValidatorLoader"]


class Loader(object):
    default_exts = ("py",)

    def __init__(self, directory, exts=None):
        self._directory = path.abspath(directory)

        if exts is not None:
            if isinstance(exts, basestring):
                exts = (exts,)
            else:
                exts = tuple(exts)
        else:
            exts = self.default_exts
        self._exts = exts
    
    def cleanup(self):
        pass

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
        for k, v in data.iteritems():
            if (k.startswith("__") and k.endswith("__") or \
                    callable(v) or isinstance(v, ModuleType)):
                continue
            ret[k] = v
        return ret

    def _run_path(self, filepath, init_globals=None):
        fullpath = self.joinpath(filepath)
        data = runpy.run_path(fullpath, init_globals)
        data = self._filter_data(data)
        return data
    
    def _load(self, filepath, extra=None):
        filepath = self._resolve_filepath(filepath)
        data = self._run_path(filepath)
        
        if extra is not None:
            data = self._extend_data(data, extra)

        return data
    
    def _extend_data(self, data, extra_data):
        data.update(extra_data)
        return data

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
            default=None,
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

        self._default = default
        self._default_data = None
    
    def cleanup(self):
        super(ConfigLoader, self).cleanup()

        self._default_data = None
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
    
    def _get_result_data(self):
        ret = {}
        if self._default_data:
            ret.update(self._default_data)
        for f in self._files_queue:
            data = self._files_data[f]
            if data:
                ret = self._extend_data(ret, data)
        return ret

    def _load(self, filepath, extra=None):
        validator = self._validator
        builder = self._builder
        default = self._default
        if default is not None:
            if isinstance(default, basestring):
                default_filepath = self._resolve_filepath(default)
                self._handle(default_filepath)
            elif isinstance(default, ModuleType):
                self._default_data = self._filter_data(vars(default))
            elif isinstance(default, dict):
                self._default_data = self._filter_data(default)
            else:
                raise TypeError("default options must be string of path to file or dict: %s", type(default))
            
        filepath = self._resolve_filepath(filepath)
        self._handle(filepath)
        
        data = self._get_result_data()
        
        if extra is not None:
            data = self._extend_data(data, extra)

        if builder:
            data = builder.build(data)
        
        if validator:
            data = validator.validate(data)

        return data

    def convert(self, data):
        return Config(data)


class ValidatorLoader(Loader):
    def _load(self, filepath, extra=None):
        filepath = self._resolve_filepath(filepath)
        data = self._run_path(filepath, LOADER_GLOBALS)
        if extra is not None:
            data = self._extend_data(data, extra)
        return data

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



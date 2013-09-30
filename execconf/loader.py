from __future__ import absolute_import
import os
from os import path
from types import ModuleType
import runpy
from tempfile import NamedTemporaryFile
from .utils import recursive_fmt
from .config import Config
from .helpers import (DummyHelper, IncludeHelper, MergeHelper,
                      MergeOptionHelper)
from .validator import Validator
from .validator.nodes import Node, Dict, LOADER_GLOBALS
from .builder import Builder
from .exceptions import (AbsPathError, NotFoundError,
                         NotFoundExtsError, UndeclaredExtError,
                         FileHandleError, CircularIncludeError,
                         UnknownFormatterError)

__all__ = ["Loader", "ConfigLoader", "ValidatorLoader"]

class Loader(object):
    defaults_exts = ("py",)

    def __init__(self, directory, exts=None, defaults=None):
        self.directory = path.abspath(directory)

        if exts is not None:
            if isinstance(exts, basestring):
                exts = (exts,)
            else:
                exts = tuple(exts)
        else:
            exts = self.defaults_exts
        self._exts = exts

        self._dummy_helper = DummyHelper()
        self._defaults = defaults
        self._data = {}
        self._resolved_filepaths = {}
        self._defaults_data = None

    def cleanup(self):
        self._data = {}

    def append_data_mixin(self, extra):
        self._data_mixins.append(extra)

    def joinpath(self, *args):
        return path.join(self.directory, *args)
    
    def _resolve_filepath_ext(self, filepath, directory=None):
        if directory is None:
            directory = self.directory

        filename, ext = path.splitext(filepath)

        if not ext:
            found_filepath = None
            for _ext in self._exts:
                check_filepath = "%s.%s" % (filepath, _ext)
                if path.exists(path.join(directory, check_filepath)):
                    found_filepath = check_filepath
                    break
            if found_filepath is None:
                raise NotFoundExtsError("file %s not found in %s with any declared extensions: %s" % (filepath, directory, ", ".join(self._exts)))

            # set new filepath
            filepath = found_filepath
        elif ext[1:] not in self._exts:
            raise UndeclaredExtError("file %s has undeclared extension %s" % (filepath, ext))
        else:
            if not path.exists(path.join(directory, filepath)):
                raise NotFoundError("file %s not found in %s" % (filepath, directory))

        return filepath

    def _resolve_filepath(self, filepath, force=False):
        ret = None
        if not force:
            try:
                resolved = self._resolved_filepaths[filepath]
            except KeyError:
                force = True
            else:
                ret = resolved
        
        if force:
            orig_filepath = filepath
            filepath = path.normpath(filepath)
            if path.isabs(filepath):
                drive, tail = path.splitdrive(filepath)
                if drive:
                    raise AbsPathError("absolute path with drive not allowed: %s" % filepath)
                filepath = filepath[1:]

            # resolve extension
            filepath = self._resolve_filepath_ext(filepath)
            
            # add to cache
            self._resolved_filepaths[orig_filepath] = filepath
            ret = filepath
        return ret
    
    def resolve_filepath(self, filepath):
        return self._resolve_filepath(filepath)
    
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

    def _run_path(self, filepath, init_globals=None, directory=None):
        if directory is None:
            directory = self.directory
        fullpath = path.join(directory, filepath)
        data = runpy.run_path(fullpath, init_globals)
        data = self._filter_data(data)
        return data
    
    def _load_defaults(self):
        defaults = self._defaults
        data = None
        if defaults is not None:
            if isinstance(defaults, basestring):
                defaults_directory, defaults_filepath = path.split(defaults)

                defaults_filepath = self._resolve_filepath_ext(defaults_filepath, 
                        directory=defaults_directory)
                data = self._run_path(defaults_filepath, 
                        directory=defaults_directory)
            elif isinstance(defaults, ModuleType):
                data = self._filter_data(vars(defaults))
            elif isinstance(defaults, dict):
                data = self._filter_data(defaults)

            if data is not None:
                self._defaults_data = data
            else:
                raise TypeError("defaults options must be string of path to file or dict or some package: %s", type(defaults))

    def _load(self, filepath, extra=None):
        self._load_defaults()

        filepath = self._resolve_filepath(filepath)
        data = self._run_path(filepath)
        self._extend_data(self._defaults_data)
        self._extend_data(data)
        
        if extra:
            self._extend_data(data, extra)

        return self._data
    
    def _extend_data(self, extra_data):
        if extra_data:
            self._data.update(extra_data)
        return self._data

    def load(self, filepath, extra=None):
        f = None
        if not isinstance(filepath, basestring):
            f = NamedTemporaryFile(mode="w",
                                   prefix="excc_",
                                   suffix=(".%s" % self._exts[0]),
                                   dir=self.directory,
                                   delete=False)
            for line in filepath.readlines():
                f.write(line)
            f.close()
            filepath = path.basename(f.name)
        
        try:
            # handler root filepath
            data = self._load(filepath, extra=extra)
        finally:
            if f:
                os.remove(f.name)

        # convert to result config data structure
        conf = self.convert(data)
        
        self.cleanup()
        return conf

    def convert(self, data):
        return data


class ConfigLoader(Loader):
    _helpers = {}

    @staticmethod
    def add_helper(helper):
        ConfigLoader._helpers[helper.NAME] = helper

    @staticmethod
    def remove_helper(helper):
        key = helper.NAME
        try:
            del ConfigLoader._helpers[key]
        except KeyError:
            pass

    def __init__(self, directory,
                 exts=None, builder=None, validator=None,
                 **kwargs):
        super(ConfigLoader, self).__init__(directory, exts=exts, **kwargs)

        if validator is not None and not isinstance(validator, Validator):
            raise TypeError("option validator must be istance of Validator")
        if builder is not None and not isinstance(builder, Builder):
            raise TypeError("option builder must be istance of Builder")
        self._validator = validator
        self._builder = builder
        
        self._included = []
        self._root_filepath = ":root:"
        self._defaults_filepath = ":defaults:"
        self._parent_filepath = self._root_filepath
        
        self._runpy_helpers = {}
        self._create_runpy_helpers()

        # alpha TODO
        self._tree = None
        self._tree_branches = {}
        self._tree_queue_branch = None
        self._create_tree_root()
    
    def cleanup(self):
        super(ConfigLoader, self).cleanup()

        self._included = []
        self._parent_filepath = self._root_filepath

        self._tree_branches = {}
        self._tree_queue_branch = None
        self._create_tree_root()

        if self._validator:
            self._validator.cleanup()
        if self._builder:
            self._builder.cleanup()
    
    def _get_tree_branch(self, filepath):
        try:
            return self._tree_branches[filepath]
        except KeyError:
            pass
        ret = [filepath, [], None, None]
        self._tree_branches[filepath] = ret
        return ret
    
    def _create_tree_root(self):
        self._tree = [self._get_tree_branch(self._root_filepath),
                      self._dummy_helper, [], {}]

    def _has_tree_branch(self, filepath):
        return filepath in self._tree_branches

    @property
    def parent_filepath(self):
        return self._parent_filepath
    
    def parent_join(self, filepath):
        return path.join(path.dirname(self._parent_filepath), filepath)

    def _get_runpy_helper_wrap(self, h):
        def wrap(*args, **kwargs):
            return h.caller(self, *args, **kwargs)
        return wrap

    def _create_runpy_helpers(self):
        for n, h in self._helpers.iteritems():
            hi = h()
            self._runpy_helpers[n] = self._get_runpy_helper_wrap(hi)

    def _handle(self, filepath, helper=None,
            helper_args=None, helper_kwargs=None):
        _included = self._included
        
        if filepath in _included:
            raise CircularIncludeError("%s already included: %s" % (filepath, "->".join(_included)))
        
        if not helper:
            helper = self._dummy_helper
        if not helper_args:
            helper_args = []
        if not helper_kwargs:
            helper_kwargs = {}
     
        parent_filepath = self._parent_filepath
        
        branch = self._get_tree_branch(filepath)
        queue_data = [branch, helper, helper_args, helper_kwargs]
        if not self._tree_queue_branch:
            if not self._tree:
                self._tree = [self._get_tree_branch(self._parent_filepath),
                              self._dummy_helper, [], {}]
            queue_branch = self._tree
        else:
            queue_branch = self._tree_queue_branch
        queue_branch[0][1].append(queue_data)

        if branch[2] is None:
            # append filepath for check cycling include
            _included.append(filepath)

            # safe previously parent_filepath
            prev_parent_filepath = self._parent_filepath
            self._parent_filepath = filepath

            prev_queue_branch = self._tree_queue_branch
            self._tree_queue_branch = queue_data

            # eval python file with helpers
            data = self._run_path(filepath, self._runpy_helpers)
            
            # return previously parent_filepath
            self._parent_filepath = prev_parent_filepath
            self._tree_queue_branch = prev_queue_branch

            # remove filepath in circular check
            _included.remove(filepath)
            
            # add data
            branch[2] = data

    def handle(self, filepath, *args, **kwargs):
        filepath = self._resolve_filepath(filepath)
        return self._handle(filepath, *args, **kwargs)
    
    def _iter_tree(self, _iner=None):
        branch = _iner or self._tree
        for b in branch[0][1]:
            for bi in self._iter_tree(_iner=b):
                yield bi
            yield branch, b

    def _collect_result_data(self):
        data = {}
        for p, c in self._iter_tree():
            pdata = p[0][3]
            if pdata is None:
                pdata = p[0][2]

            cdata = c[0][3]
            if cdata is None:
                cdata = c[0][2]
                if cdata is None:
                    cdata = {}
            if not pdata:
                data = cdata.copy()
            else:
                data = c[1].merge(pdata, cdata, *c[2], **c[3])
            p[0][3] = data
        self._data = data
    
    def _load_defaults(self):
        super(ConfigLoader, self)._load_defaults()

        branch = self._get_tree_branch(self._defaults_filepath)
        branch[2] = self._defaults_data
        self._tree[0][1].insert(0, [branch, self._dummy_helper, [], {}])

    def _load(self, filepath, extra=None):
        self._load_defaults()

        validator = self._validator
        builder = self._builder
         
        filepath = self._resolve_filepath(filepath)
        self._handle(filepath)
        
        self._collect_result_data()
        
        if extra:
            self._extend_data(extra)

        data = self._data
        if builder:
            data = builder.build(data)
        
        if validator:
            data = validator.validate(data)

        self._data = data
        return data

    def convert(self, data):
        replacement = data.pop("EXEC_REPLACEMENT", None)
        if replacement is not None:
            data = recursive_fmt(data, replacement)

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


# Built-in helpers
ConfigLoader.add_helper(IncludeHelper)
ConfigLoader.add_helper(MergeHelper)
ConfigLoader.add_helper(MergeOptionHelper)



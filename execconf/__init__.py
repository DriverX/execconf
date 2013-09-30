from __future__ import absolute_import
import argparse 
import sys
import os
from os import path
from tempfile import NamedTemporaryFile
from .config import Config
from .validator import Validator
from .validator.nodes import CLI_TYPES
from .builder import Builder
from .loader import Loader, ConfigLoader, ValidatorLoader

__version__ = (0, 3, 4)

__all__ = ["Config", "Validator", "Builder", "Loader", "ConfigLoader",
           "ValidatorLoader"]

def version():
    return ".".join(map(str, __version__))

def cli_parser():
    parser = argparse.ArgumentParser(
            description="Execconf config generator")
    parser.add_argument("-v", "--version",
                        action='version',
                        version=('execonf %s' % version()))

    def path_type(v):
        v = path.normpath(v)
        if not path.exists(v):
            raise IOError("%s is not exists" % v)
        return v

    parser.add_argument("-i", "--input",
                        type=path_type,
                        help="from file. If not set, read from stdin")
    parser.add_argument("-d", "--defaults",
                        help="defaults options file")
    parser.add_argument("-a", "--validate",
                        type=path_type,
                        help="validation file")
    parser.add_argument("-o", "--output",
                        # type=path_type,
                        help="write result to output file. If not set, result write to stdout")
    parser.add_argument("-t", "--type",
                        default="json",
                        choices=("json", "yaml"),
                        help="format output data")
    parser.add_argument("--yaml-canonical",
                        action="store_true",
                        help="use canonical YAML format")
    parser.add_argument("--json-ugly",
                        action="store_true",
                        help="not use pretty print JSON formation")
    parser.add_argument("--root-dir",
                        type=path_type,
                        help="""use this if set data in stdin.
Ex: $ echo 'FOO=True' | execconf -i /some/dir""")
    parser.add_argument("-x", "--extension",
                        nargs="+",
                        default="py",
                        help="extension check for input file and inner helpers")
    parser.add_argument("-e", "--extra",
                        nargs=3,
                        action="append",
                        metavar=("KEY", "VALUE", "VALIDATE"),
                        help=("extra options. Validation types: %s" % ",".join(CLI_TYPES.keys())))
    
    # parse sys.argv
    return parser
    
def cli_namespace(args):
    args = vars(args)

    # filepath
    filepath = None
    directory = None

    ns_input = args.get("input")
    if ns_input:
        directory, filepath = path.split(ns_input) 
    else:
        filepath = sys.stdin
    
    # output
    output = None
    ns_output = args.get("output")
    if ns_output:
        output = open(ns_output, "w")
    else:
        output = sys.stdout

    # override directory
    root_dir = args.get("root_dir")
    temp_file = None
    if root_dir:
        if ns_input:
            # Do this because directory set to Loader as constantly
            with open(ns_input, "wb") as f:
                temp_file = NamedTemporaryFile(mode="w",
                                               prefix="excc_",
                                               suffix=filepath,
                                               dir=root_dir,
                                               delete=False)
                temp_file.write(f.read())
                temp_file.close()
                filepath = path.basename(temp_file.name)
                directory = root_dir
        else:
            directory = root_dir
    else:
        if not ns_input:
            raise ValueError("if use stdin --root-dir must be specified")
       
    # defaults file
    defaults = args.get("defaults")
    
    # exts
    exts = args.get("extension")

    # extra options
    extra_data = {}
    extras = args.get("extra")
    if extras:
        for extra in extras:
            key, value, vtype = extra
            try:
                check = CLI_TYPES[vtype]
            except KeyError:
                raise ValueError("unknown validation type %s" % vtype)
            else:
                extra_data[key] = check.check(value)

    # validation
    validator = None
    validate = args.get("validate")
    if validate:
        validate_dirname, validate_filepath = path.split(validate)
        validator_loader = ValidatorLoader(validate_dirname, exts=exts)
        validator = validator_loader.load(validate_filepath)

    try:
        loader = ConfigLoader(directory,
                              exts=exts,
                              defaults=defaults,
                              validator=validator)
        conf = loader.load(filepath, extra=extra_data)
    except:
        raise
    else:
        # formatter
        formatter = args.get("type")
        formatter_kw = {}
        if formatter == "yaml":
            if args.get("yaml_canonical", False):
                formatter_kw["canonical"] = True
            result = conf._to_yaml(**formatter_kw)
        elif formatter == "json":
            if args.get("json_ugly", False):
                formatter_kw["pretty_print"] = False
            result = conf._to_json(**formatter_kw)

        # write result to stream
        output.write(result)
        output.write("\n")
    finally:
        # remove temp_file
        if temp_file:
            os.remove(temp_file.name)
        # stdout not need close
        if ns_output:
            output.close()

def main():
    parser = cli_parser()
    args = parser.parse_args()
    cli_namespace(args)


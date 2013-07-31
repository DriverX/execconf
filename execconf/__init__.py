from __future__ import absolute_import
import argparse 
import sys
import os
from os import path
from tempfile import NamedTemporaryFile
from .config import Config
from .validator import Validator
from .builder import Builder
from .loader import Loader, ConfigLoader, ValidatorLoader

__version__ = (0, 3, 1)

__all__ = ["Config", "Validator", "Builder", "Loader", "ConfigLoader",
           "ValidatorLoader"]

def version():
    return ".".join(map(str, __version__))

def main():
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
    parser.add_argument("-o", "--output",
                        # type=path_type,
                        help="write result to output file. If not set, result write to stdout")
    parser.add_argument("-t", "--type",
                        default="json",
                        choices=("json", "yaml", "pickle"),
                        help="format output data")
    parser.add_argument("--root-dir",
                        type=path_type,
                        help="""use this if set data in stdin.
Ex: $ echo 'FOO=True' | execconf -i /some/dir""")
    parser.add_argument("--extension",
                        nargs="+",
                        default="py",
                        help="extension check for input file and inner helpers")
    
    # parse sys.argv
    args = parser.parse_args()
    
    # filepath
    filepath = None
    directory = None
    if args.input:
        directory, filepath = path.split(args.input) 
    else:
        filepath = sys.stdin
    
    # output
    output = None
    if args.output:
        output = open(args.output, "w")
    else:
        output = sys.stdout
    
    # formatter
    formatter = args.type

    # override directory
    root_dir = args.root_dir
    temp_file = None
    if root_dir:
        if args.input:
            # Do this because directory set to Loader as constantly
            with open(args.input, "wb") as f:
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
        if not args.input:
            raise ValueError("if use stdin --root-dir must be specified")
       
    # exts
    exts = args.extension
    
    try:
        loader = ConfigLoader(directory, exts=exts, formatter=formatter)
        result = loader.load(filepath)
    except:
        raise
    else:
        # write result to stream
        output.write(result)
        output.write("\n")
    finally:
        # remove temp_file
        if temp_file:
            os.remove(temp_file.name)
        # stdout not need close
        if args.output:
            output.close()



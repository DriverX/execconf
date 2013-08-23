#!/usr/bin/env python

from os import path, walk
from setuptools import setup
from execconf import __version__

MODULE_ROOT = path.dirname(path.abspath(__file__))

def get_tests_data():
    package_path = path.join(MODULE_ROOT, "execconf", "tests")
    data = []
    data_root = path.join(package_path, "data")
    for r, d, f in walk(data_root):
        data_dir = path.relpath(r, package_path)
        for _f in f:
            data.append(path.join(data_dir, _f))
    return data

setup(name="execconf",
      version=".".join(map(str, __version__)),
      description="Executable config on pure python",
      author="Anton Ilyushenkov",
      author_email="me@driverx.ru",
      url="https://github.com/DriverX/execconf",
      license="http://opensource.org/licenses/MIT",
      packages=["execconf",
                "execconf.tests",
                "execconf.validator"],
      include_package_data=True,
      # package_data={"execconf.tests": get_tests_data()},
      scripts=["bin/execconf"],
      test_suite="execconf.tests.all_tests_suite",
      classifiers=["License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Intended Audience :: System Administrators",
                   "Operating System :: Unix",
                   "Topic :: Utilities"]
      )


import unittest
import sys
import os
from os import path
from StringIO import StringIO
import json
try:
    import yaml
except ImportError:
    yaml = None
import pickle
from execconf import (ConfigLoader as Loader, ValidatorLoader,
                      Validator, Builder)
from execconf.exceptions import (AbsPathError, NotFoundError,
                                 NotFoundExtsError, UndeclaredExtError,
                                 CircularIncludeError, UnknownFormatterError)
import data_defaults

MODULE_ROOT = path.dirname(path.abspath(__file__))

class TestLoader(unittest.TestCase):
    def test_load(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("base.py")
        conf3 = loader1.load("default.py")
        
        loader2 = Loader(path.join(MODULE_ROOT, "data"))
        conf2 = loader2.load("include.py")

        loader3 = Loader(path.join(MODULE_ROOT, "data"))
        
        self.assertEqual(len(conf1), 4)
        self.assertEqual(conf1.FOO, "BAR")
        self.assertEqual(conf1["BAZ"], 123)
        self.assertTrue(isinstance(conf1.QUX, tuple))
        self.assertEqual(len(conf1.QUX), 1)
        self.assertEqual(conf1.QUX[0], "Hello")

        self.assertTrue("TEST" in conf2)
        self.assertEqual(conf2.TEST, 42)
        self.assertEqual(conf2["FOO"], "BAR")
        self.assertEqual(conf2.BLA["bla"], "blabla")
        self.assertEqual(conf2.BAZ, 123)
        self.assertEqual(conf2.QUX[0], "Hello")
        self.assertFalse("key1" in conf2.MERGE)
        self.assertTrue("key2" in conf2.MERGE)
        self.assertEqual(conf2.MERGE["key2"], "value2")

        self.assertTrue(conf3.DEFAULT)
        self.assertFalse(conf3.FOO)

        with self.assertRaises(NotFoundError) as cm:
            loader2.load("notfound.py")
        
        if sys.platform == "win32": 
            with self.assertRaises(AbsPathError) as cm:
                loader2.load("except_abspath.py")

    def test_load_with_defaults(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"),
                defaults=path.join(MODULE_ROOT, "data", "default.py"))
        conf1 = loader1.load("base.py")
        conf2 = loader1.load("base2.py")

        loader2 = Loader(path.join(MODULE_ROOT, "data"),
                defaults={
                    "DEFAULT_DICT": True,
                    "FOO": False,
                    "__will_be_remove__": True})
        conf3 = loader2.load("base.py")
        conf4 = loader2.load("base2.py")

        loader3 = Loader(path.join(MODULE_ROOT, "data"),
                defaults="notfound.py")

        loader4 = Loader(path.join(MODULE_ROOT, "data"),
                defaults=[])
        
        loader5 = Loader(path.join(MODULE_ROOT, "data"),
                defaults=data_defaults)
        conf5 = loader5.load("base.py")
        
        self.assertEqual(len(conf1), 5)
        self.assertTrue(conf1.DEFAULT)
        self.assertEqual(conf1.FOO, "BAR")

        self.assertEqual(len(conf2), 3)
        self.assertTrue(conf2.DEFAULT)
        self.assertEqual(conf2.FOO, "BAZ")
        self.assertTrue("BASE1" not in conf2)
        self.assertTrue(conf2.BASE2)

        self.assertEqual(len(conf3), 5)
        self.assertTrue(conf3.DEFAULT_DICT)
        self.assertEqual(conf3.FOO, "BAR")

        self.assertEqual(len(conf4), 3)
        self.assertTrue(conf4.DEFAULT_DICT)
        self.assertEqual(conf4.FOO, "BAZ")
        self.assertTrue("BASE1" not in conf4)
        self.assertTrue(conf4.BASE2)

        self.assertEqual(len(conf5), 5)
        self.assertTrue(conf5.DEFAULT)
        self.assertEqual(conf5.FOO, "BAR")

        with self.assertRaises(NotFoundError) as cm:
            loader3.load("base.py")

        with self.assertRaisesRegexp(TypeError, "defaults options must be") as cm:
            loader4.load("base.py")
    
    def test_exts(self):
        loader = Loader(path.join(MODULE_ROOT, "data"),
                exts=["txt", "md", "js", "py"])
        conf = loader.load("exts")
        loader2 = Loader(path.join(MODULE_ROOT, "data"),
                exts=["txt"])
        
        self.assertTrue(conf.EXT_TXT)
        self.assertTrue(conf.EXT_MD)
        self.assertTrue(conf.EXT_PRIOR, "js")
        self.assertTrue(conf.EXT_EXISTS, "py")

        with self.assertRaises(UndeclaredExtError) as cm:
            loader2.load("exts.py")
        
        with self.assertRaises(NotFoundExtsError) as cm:
            loader2.load("exts_except")       

    def test_deepload(self):
        loader = Loader(path.join(MODULE_ROOT, "data"))
        conf = loader.load("deepload.py")
        
        loader2 = Loader(path.join(MODULE_ROOT, "data"))

        self.assertEqual(conf.FOO, "BAR")
        self.assertTrue(conf.DEEP1)
        self.assertTrue(conf.DEEP2)
        self.assertTrue(conf.DEEP3)
        self.assertTrue(conf.DEEP4)
        self.assertTrue(conf.DEEP5)
        self.assertEqual(conf.DEEP55, 2)
        self.assertTrue(conf.DEEP6)
        self.assertTrue(conf.LAST) 

        with self.assertRaises(CircularIncludeError) as cm:
            loader2.load("deepload_except")
    
    # TODO
    def test_validator(self):
        pass

    def test_builder(self):
        class Builder1(Builder):
            def build(self, data):
                ret = data.copy()
                ret["FOO"] = "BUILD"
                return ret
                    
        loader1 = Loader(path.join(MODULE_ROOT, "data"), builder=Builder1())
        conf1 = loader1.load("base.py")
        self.assertEqual(len(conf1), 4)
        self.assertEqual(conf1.FOO, "BUILD")
        self.assertEqual(conf1["BAZ"], 123)

    def test_extra_data(self):
        loader = Loader(path.join(MODULE_ROOT, "data"))
        conf = loader.load("base.py", extra={"QUX": ["World"], "NEW": 1})

        self.assertEqual(len(conf), 5)
        self.assertEqual(conf.QUX[0], "World")
        self.assertEqual(conf.NEW, 1)

    def test_filter_data(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("filter.py")

        self.assertEqual(len(conf1), 2)
        self.assertEqual(conf1.FILTER, True)
        self.assertTrue("APPROVE_DICT" in conf1)

    def test_load_merge(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("merge")

        self.assertEqual(len(conf1), 7)
        self.assertTrue(conf1.MERGE)
        
        self.assertEqual(len(conf1.OPT1), 3)
        self.assertEqual(conf1.OPT1["FOO"], 1)
        self.assertEqual(conf1.OPT1["BAR"], 22)
        self.assertEqual(conf1.OPT1["BAZ"], 33)
        
        self.assertEqual(len(conf1.OPT2), 2)
        self.assertEqual(conf1.OPT2[0], 11)
        
        self.assertEqual(len(conf1.OPT3), 4)
        self.assertEqual(len(conf1.OPT3["FOO"]), 2)
        self.assertEqual(conf1.OPT3["FOO"]["BAR"], 1)
        self.assertEqual(conf1.OPT3["FOO"]["BARR"], 2)
        self.assertTrue(isinstance(conf1.OPT3["BAZ"], tuple))
        self.assertEqual(len(conf1.OPT3["BAZ"]), 1)
        self.assertTrue(conf1.OPT3["SOME1"])
        self.assertTrue(conf1.OPT3["SOME2"])
        
        self.assertEqual(len(conf1.OPT4), 4)
        self.assertEqual(conf1.OPT4["FOO"], 1)
        self.assertEqual(conf1.OPT4["BAR"], 22)
        
        self.assertTrue(isinstance(conf1.OPT5, dict))
        self.assertEqual(len(conf1.OPT5), 1)
        
        self.assertEqual(conf1.OPT6, "FOO")
    
    def test_load_merge_option(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("merge_option")

        self.assertEqual(len(conf1), 8)
        self.assertTrue(conf1.MERGE)
        
        self.assertEqual(len(conf1.OPT1), 4)
        self.assertEqual(len(conf1.OPT1["BAR"]), 2)
        self.assertEqual(conf1.OPT1["BAR"]["BAZ"], 2)
        self.assertEqual(conf1.OPT1["BAR"]["BAZZ"], 22)
        self.assertEqual(conf1.OPT1["QUX"], 33)
        
        self.assertTrue("LVL1_KEY1" in conf1.OPT2)
        self.assertTrue("LVL1_KEY2" in conf1.OPT2)
        self.assertTrue("LVL2_KEY1" not in conf1.OPT2["LVL1"])
        self.assertTrue("LVL2_KEY2" in conf1.OPT2["LVL1"])
        
        self.assertTrue("LVL1_KEY1" in conf1.OPT3)
        self.assertTrue("LVL1_KEY2" in conf1.OPT3)
        self.assertTrue("LVL2_KEY1" in conf1.OPT3["LVL1"])
        self.assertTrue("LVL2_KEY2" in conf1.OPT3["LVL1"])
        self.assertTrue("LVL3_KEY1" in conf1.OPT3["LVL1"]["LVL2"])
        self.assertTrue("LVL3_KEY2" in conf1.OPT3["LVL1"]["LVL2"])
        self.assertTrue("LVL4_KEY1" not in conf1.OPT3["LVL1"]["LVL2"]["LVL3"])
        self.assertTrue("LVL4_KEY2" in conf1.OPT3["LVL1"]["LVL2"]["LVL3"])
        
        self.assertEqual(len(conf1.OPT4), 2)
        self.assertTrue("FOO" in conf1.OPT4)
        self.assertTrue("BAR" in conf1.OPT4)
        self.assertEqual(conf1.OPT4["BAR"], 222)
        
        self.assertEqual(conf1.OPT5, "FOO")
        
        self.assertEqual(conf1.OPT6, 12321)
        
        self.assertEqual(conf1.OPT7, True)
        self.assertTrue("OPT8" not in conf1)

    def test_complex_helpers(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("complex_helpers")

        self.assertEqual(len(conf1), 10)
        self.assertTrue(conf1.COMPLEX)
        self.assertTrue(conf1.COMPLEX_INCLUDE)
        self.assertTrue(conf1.COMPLEX_MERGE)
        self.assertTrue(conf1.COMPLEX_MERGE_OPTION)

        self.assertEqual(conf1.FOO, 111)
        self.assertEqual(conf1.BAR, 22)
        self.assertEqual(conf1.BAZ, 333)

        self.assertEqual(len(conf1.MERGE_INCLUDE), 3)
        self.assertTrue("FOO" not in conf1.MERGE_INCLUDE)
        self.assertEqual(conf1.MERGE_INCLUDE["BAR"], 22)
        self.assertEqual(conf1.MERGE_INCLUDE["BAZ"], 333)
        self.assertEqual(conf1.MERGE_INCLUDE["QUX"], 4444)

        self.assertEqual(len(conf1.MERGE_OPTION1), 2)
        self.assertEqual(conf1.MERGE_OPTION1["FOO"], "BAR")
        self.assertEqual(conf1.MERGE_OPTION1["BAZ"], "QUX")
        
        self.assertEqual(len(conf1.MERGE_OPTION2), 2)
        self.assertEqual(conf1.MERGE_OPTION2["FOO"], "BAR")
        self.assertTrue("QUX" not in conf1.MERGE_OPTION2["BAZ"])
        self.assertTrue(conf1.MERGE_OPTION2["BAZ"]["QUXX"])

    def test_load_file(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))

        f = StringIO("FILE=True\ninclude('base2')")
        conf1 = loader1.load(f)
        f.close()

        self.assertEqual(len(conf1), 3)
        self.assertEqual(conf1.FOO, "BAZ")
        self.assertTrue(conf1.BASE2)
        self.assertTrue(conf1.FILE)

    def test_formatters(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("base2")._to_json()
        
        if yaml:
            loader2 = Loader(path.join(MODULE_ROOT, "data"))
            conf2 = loader2.load("base2")._to_yaml()
        else:
            loader2 = Loader(path.join(MODULE_ROOT, "data"))
            conf2 = loader2.load("base2")
            with self.assertRaises(NotImplementedError):
                conf2._to_yaml()
    
        self.assertTrue(json.loads(conf1)["BASE2"])
        if yaml:
            self.assertTrue(yaml.load(conf2)["BASE2"])

    def test_replacement(self):
        loader1 = Loader(path.join(MODULE_ROOT, "data"))
        conf1 = loader1.load("replacement")
        
        loader2 = Loader(path.join(MODULE_ROOT, "data"))
        conf2 = loader2.load("no_replacement")

        self.assertEqual(len(conf1), 6)
        self.assertEqual(conf1.FOO, "FOO bar baz")
        self.assertEqual(conf1.BAR, "FOO BAR baz")

        res = conf1.LIST
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "FOO")
        self.assertEqual(res[1], "BAR")
        self.assertEqual(res[2], 123)

        self.assertEqual(conf1.ANOTHER_FMT, "%(some)s")
        self.assertEqual(conf1.FMT, "%(new_fmt)s")

        self.assertEqual(len(conf2), 2)
        self.assertEqual(conf2.FMT, "%%(some)s")




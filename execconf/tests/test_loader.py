import unittest
import sys
import os
from os import path
from execconf import ConfigLoader as Loader, ValidatorLoader, Validator, Builder
from execconf.exceptions import AbsPathError, NotFoundError, \
                                NotFoundExtsError, UndeclaredExtError, \
                                CircularIncludeError
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
        loader1 = Loader(path.join(MODULE_ROOT, "data"), defaults="default.py")
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









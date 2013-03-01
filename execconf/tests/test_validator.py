import unittest
import os
from os import path
from execconf import Validator, ValidatorLoader as Loader, \
                     ConfigLoader
from execconf.validator.nodes import Boolean, Integer, Float, String, List, \
                                     ListBoolean, ListInteger, ListFloat, \
                                     ListString, ListDict, Dict, Option, \
                                     Pass
from execconf.exceptions import ValidatorConvertError, ValidatorCheckError 


MODULE_ROOT = path.dirname(path.abspath(__file__))
VALID_ROOT = path.join(MODULE_ROOT, "data/validator")

class TestValidator(unittest.TestCase):
    def test_validate(self):
        v1 = Validator(Dict({
            "FOO": String(),
            "BAR": Boolean()
        }))

        data1 = v1.validate({
            "FOO": "STR",
            "BAR": "ON"
        })
        self.assertEqual(data1["FOO"], "STR")
        self.assertEqual(data1["BAR"], True)
        with self.assertRaises(ValidatorConvertError) as cm:
            v1.validate({
                "FOO": 1    
            })
        with self.assertRaises(ValidatorConvertError) as cm:
            v1.validate({
                "BAR": "onn"    
            })


class TestValidatorLoader(unittest.TestCase):
    def test_load(self):
        loader1 = Loader(VALID_ROOT)
        v1 = loader1.load("simple_config.validate.py")
        conf_loader1 = ConfigLoader(VALID_ROOT)
        conf1 = conf_loader1._load("simple_config.py")

        data1 = v1.validate(conf1)
        
        self.assertEqual(data1["BOOL_TRUE"], True)
        self.assertEqual(data1["BOOL_TRUE_INT"], True)
        self.assertEqual(data1["BOOL_TRUE_STR1"], True)
        self.assertEqual(data1["BOOL_TRUE_STR2"], True)
        self.assertEqual(data1["BOOL_FALSE"], False)
        self.assertEqual(data1["BOOL_FALSE_INT"], False)
        self.assertEqual(data1["BOOL_FALSE_STR1"], False)
        self.assertEqual(data1["BOOL_FALSE_STR2"], False)

        self.assertTrue(isinstance(data1["STR"], unicode))
        self.assertEqual(data1["STR"], "some string")
        self.assertEqual(data1["STR_UNICODE"], "some unicode string")

        self.assertTrue(isinstance(data1["INT"], int))
        self.assertEqual(data1["INT"], 123)
        self.assertEqual(data1["INT_FLOAT"], 123)

        self.assertTrue(isinstance(data1["FLOAT"], float))
        self.assertEqual(data1["FLOAT"], 123.456)
        self.assertEqual(data1["FLOAT_INT"], 123.0)

        self.assertEqual(len(data1["LIST"]), 3)
        self.assertEqual(len(data1["LIST_TUPLE"]), 3)
        
        self.assertEqual(data1["LIST_BOOL"][0], True)
        self.assertEqual(data1["LIST_BOOL"][1], True)
        self.assertEqual(data1["LIST_BOOL"][2], True)
        self.assertEqual(data1["LIST_BOOL"][3], False)
        self.assertEqual(data1["LIST_BOOL"][4], False)
        self.assertEqual(data1["LIST_BOOL"][5], False)

        self.assertEqual(data1["LIST_INT"][0], 1)
        self.assertEqual(data1["LIST_INT"][1], 2)

        self.assertEqual(data1["LIST_FLOAT"][0], 1.0)
        self.assertEqual(data1["LIST_FLOAT"][1], 2.3)

        self.assertEqual(data1["LIST_STR"][0], u"foo")
        self.assertEqual(data1["LIST_STR"][1], u"bar")

        self.assertEqual(data1["DICT"]["BOOL"], True)
        self.assertEqual(data1["DICT"]["STR"], u"some string")
        self.assertEqual(data1["DICT"]["INT"], 123)
        self.assertEqual(data1["DICT"]["FLOAT"], 123.456)
        
        self.assertEqual(data1["OPTION1"], "bar")
        self.assertEqual(data1["OPTION2"], 2)

        self.assertEqual(data1["PASS"], "ololo")

        self.assertEqual(data1["OTHER"], "OTHER")






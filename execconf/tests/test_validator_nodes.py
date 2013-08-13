import unittest
from execconf.validator.nodes import Boolean, Integer, Float, String, List, \
                                     ListBoolean, ListInteger, ListFloat, \
                                     ListString, ListDict, Dict, Option, \
                                     Pass
from execconf.exceptions import ValidatorConvertError, ValidatorCheckError, \
                                ValidatorNodeError


class TestValidatorNodes(unittest.TestCase):
    def test_boolean(self):
        node = Boolean()
        node2 = Boolean(True)
        node3 = Boolean(eq=False)

        self.assertTrue(node.check(True))
        self.assertTrue(node.check("true"))
        self.assertTrue(node.check("on"))
        self.assertTrue(node.check(1))

        self.assertFalse(node.check(False))
        self.assertFalse(node.check("false"))
        self.assertFalse(node.check("off"))
        self.assertFalse(node.check(0))

        # test case insensivity
        self.assertTrue(node.check("TrUe"))
        self.assertFalse(node.check("fAlSe"))
        
        with self.assertRaises(ValidatorConvertError) as cm:
            node.check("foo")
        with self.assertRaises(ValidatorConvertError) as cm:
            node.check(2)
        
        self.assertTrue(node2.check(1))
        self.assertFalse(node3.check("false"))
        with self.assertRaises(ValidatorCheckError) as cm:
            node2.check(False)
        with self.assertRaises(ValidatorCheckError) as cm:
            node3.check(True)

    def test_string(self):
        node1 = String()
        node2 = String("bar")
        node3 = String(eq="bar")
        node4 = String(min=4)
        node5 = String(max=4)
        node6 = String(min=3, max=4)

        with self.assertRaises(AssertionError):
            String(min=-1)
        with self.assertRaises(AssertionError):
            String(max=0)
        with self.assertRaises(AssertionError):
            String(min=2, max=1)

        self.assertEqual(node1.check("foo"), "foo")
        self.assertTrue(isinstance(node1.check("foo"), unicode))
        with self.assertRaises(ValidatorConvertError) as cm:
            node1.check(123)
        
        self.assertEqual(node2.check("bar"), "bar")
        with self.assertRaisesRegexp(ValidatorCheckError, "not equal") as cm:
            node2.check("foo")
        
        self.assertEqual(node3.check("bar"), "bar")
        with self.assertRaisesRegexp(ValidatorCheckError, "not equal") as cm:
            node3.check("foo")
        
        self.assertEqual(node4.check("fooo"), "fooo")
        with self.assertRaisesRegexp(ValidatorCheckError, "too short") as cm:
            node4.check("foo")
        
        self.assertEqual(node5.check("fooo"), "fooo")
        with self.assertRaisesRegexp(ValidatorCheckError, "too long") as cm:
            node5.check("foooo")
        
        self.assertEqual(node6.check("foo"), "foo")
        self.assertEqual(node6.check("fooo"), "fooo")
        with self.assertRaisesRegexp(ValidatorCheckError, "too short") as cm:
            node6.check("fo")
        with self.assertRaisesRegexp(ValidatorCheckError, "too long") as cm:
            node6.check("foooo")

    def test_integer(self):
        node1 = Integer()
        node2 = Integer(123)
        node3 = Integer(eq=123)
        node4 = Integer(lt=2)
        node5 = Integer(lte=2)
        node6 = Integer(gt=2)
        node7 = Integer(gte=2)
        node8 = Integer(gt=1, lt=3)
        node9 = Integer(gt=1, lte=3)
        node10 = Integer(gte=1, lt=3)
        node11 = Integer(gte=1, lte=3)
        node12 = Integer(min=3)
        node13 = Integer(max=3)
        node14 = Integer(min=3, max=3)
        
        with self.assertRaises(AssertionError):
            Integer(eq=0, lt=3)
        with self.assertRaises(AssertionError):
            Integer(eq=0, lte=3)
        with self.assertRaises(AssertionError):
            Integer(eq=0, gt=1)
        with self.assertRaises(AssertionError):
            Integer(eq=0, gte=1)
        with self.assertRaises(AssertionError):
            Integer(lt=3, lte=3)
        with self.assertRaises(AssertionError):
            Integer(gt=3, gte=3)
        with self.assertRaises(AssertionError):
            Integer(min=3, max=1)

        self.assertEqual(node1.check(123), 123)
        self.assertTrue(isinstance(node1.check(123.0), int))
        self.assertEqual(node1.check(-123.5), -123)
        self.assertEqual(node1.check("123"), 123)
        with self.assertRaises(ValidatorConvertError):
            node1.check("")
        with self.assertRaises(ValidatorConvertError):
            node1.check(None)
        with self.assertRaises(ValidatorConvertError):
            node1.check("foo")
        
        self.assertEqual(node2.check(123), 123)
        with self.assertRaisesRegexp(ValidatorCheckError, "not equal"):
            node2.check(124)
        
        self.assertEqual(node3.check(123), 123)
        with self.assertRaisesRegexp(ValidatorCheckError, "not equal 123"):
            node3.check(124)

        self.assertEqual(node4.check(1), 1)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less than 2"):
            node4.check(2)
        
        self.assertEqual(node5.check(2), 2)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less and not equal than 2"):
            node5.check(3)
        
        self.assertEqual(node6.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater than 2"):
            node6.check(2)
        
        self.assertEqual(node7.check(2), 2)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater and not equal than 2"):
            node7.check(1)

        self.assertEqual(node8.check(2), 2)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater than 1"):
            node8.check(1)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less than 3"):
            node8.check(3)

        self.assertEqual(node9.check(2), 2)
        self.assertEqual(node9.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater than 1"):
            node9.check(1)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less and not equal than 3"):
            node9.check(4)

        self.assertEqual(node10.check(1), 1)
        self.assertEqual(node10.check(2), 2)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater and not equal than 1"):
            node10.check(0)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less than 3"):
            node10.check(3)

        self.assertEqual(node11.check(1), 1)
        self.assertEqual(node11.check(2), 2)
        self.assertEqual(node11.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "not greater and not equal than 1"):
            node11.check(0)
        with self.assertRaisesRegexp(ValidatorCheckError, "not less and not equal than 3"):
            node11.check(4)
        
        self.assertEqual(node12.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node12.check(2)
        
        self.assertEqual(node13.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node13.check(4)
        
        self.assertEqual(node14.check(3), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node14.check(2)
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node14.check(4)

    def test_float(self):
        """
        More tests not needed, because Float subclass of Integer
        """

        node1 = Float()
        node2 = Float(precision=2)

        with self.assertRaises(AssertionError):
            Float(precision=-1)

        self.assertTrue(isinstance(node1.check(1), float))
        self.assertEqual(node1.check(1.2), 1.2)
        self.assertEqual(node1.check("1.2"), 1.2)
        self.assertEqual(node1.check("1"), 1.0)
        with self.assertRaises(ValidatorConvertError):
            node1.check("")
        with self.assertRaises(ValidatorConvertError):
            node1.check(None)
        with self.assertRaises(ValidatorConvertError):
            node1.check("foo")
        
        self.assertEqual(node2.check(12.3456), 12.34)
        self.assertEqual(node2.check(12), 12.0)

    def test_list(self):
        node1 = List()
        node2 = List(min=3)
        node3 = List(max=3)
        node4 = List(min=3, max=3)
        node5 = List(force=True)
        
        with self.assertRaises(AssertionError):
            List(min=-1)
        with self.assertRaises(AssertionError):
            List(max=0)
        with self.assertRaises(AssertionError):
            List(min=2, max=1)
        
        self.assertTrue(isinstance(node1.check(("foo",)), list))
        node1check = node1.check(["foo", 1, True])
        self.assertEqual(node1check[0], "foo")
        self.assertEqual(node1check[1], 1)
        self.assertEqual(node1check[2], True)
        with self.assertRaises(ValidatorConvertError):
            node1.check("foo")
        with self.assertRaises(ValidatorConvertError):
            node1.check(123)
        with self.assertRaises(ValidatorConvertError):
            node1.check({})
        
        self.assertEqual(len(node2.check([1,2,3])), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node2.check([1,2])
        
        self.assertEqual(len(node3.check([1,2,3])), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node3.check([1,2,3,4])

        self.assertEqual(len(node4.check([1,2,3])), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node4.check([1,2])
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node4.check([1,2,3,4])

        self.assertTrue(isinstance(node5.check("foo"), list))
        self.assertEqual(len(node5.check("foo")), 1)
        self.assertEqual(node5.check("foo")[0], "foo")

    def test_list_boolean(self):
        node1 = ListBoolean()
        node2 = ListBoolean(force=True)

        node1check = node1.check([True, 1, "on", False, 0, "off"])
        self.assertEqual(len(node1check), 6)
        self.assertTrue(node1check[0])
        self.assertTrue(node1check[1])
        self.assertTrue(node1check[2])
        self.assertFalse(node1check[3])
        self.assertFalse(node1check[4])
        self.assertFalse(node1check[5])
        with self.assertRaises(ValidatorConvertError):
            node1.check(["foo"])

        self.assertTrue(node2.check("on")[0])

    def test_list_integer(self):
        node1 = ListInteger()

        node1check = node1.check([1, 12.34])
        self.assertEqual(len(node1check), 2)
        self.assertEqual(node1check[0], 1)
        self.assertTrue(isinstance(node1check[1], int))
        self.assertEqual(node1check[1], 12)
        with self.assertRaises(ValidatorConvertError):
            node1.check(["foo"])

    def test_list_float(self):
        node1 = ListFloat()

        node1check = node1.check([1, 12.34])
        self.assertEqual(len(node1check), 2)
        self.assertTrue(isinstance(node1check[0], float))
        self.assertEqual(node1check[0], 1.0)
        self.assertEqual(node1check[1], 12.34)
        with self.assertRaises(ValidatorConvertError):
            node1.check(["foo"])

    def test_list_string(self):
        node1 = ListString()
        
        node1check = node1.check(["foo", "bar"])
        self.assertEqual(len(node1check), 2)
        self.assertTrue(isinstance(node1check[0], unicode))
        self.assertEqual(node1check[0], "foo")
        self.assertEqual(node1check[1], "bar")
        with self.assertRaises(ValidatorConvertError):
            node1.check([12.34])

    def test_list_dict(self):
        node1 = ListDict()

        node1check = node1.check([{"foo": 1}, {"bar": True, "baz": "qux"}])
        self.assertEqual(len(node1check), 2)
        self.assertTrue(isinstance(node1check[0], dict))
        self.assertEqual(node1check[0]["foo"], 1)
        self.assertEqual(node1check[1]["bar"], True)
        self.assertEqual(node1check[1]["baz"], "qux")
        with self.assertRaises(ValidatorConvertError):
            node1.check([12.34])

    def test_list_mixed(self):
        node1 = List([Boolean(), String()])
        node2 = List([Boolean(), String()], loop=False)

        node1check = node1.check(["true", "on", "off", "foo"])
        self.assertTrue(len(node1check), 4)
        self.assertEqual(node1check[0], True)
        self.assertTrue(isinstance(node1check[1], unicode))
        self.assertEqual(node1check[1], "on")
        self.assertEqual(node1check[2], False)
        self.assertEqual(node1check[3], "foo")

        node2check = node2.check([True, "foo"])
        self.assertTrue(len(node2check), 2)
        self.assertEqual(node2check[0], True)
        self.assertEqual(node2check[1], "foo")
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than declared checks 2"):
            node2.check([True, "foo", False])

    def test_dict(self):
        some_dict = {"foo": 1.2, "bar": True, "baz": "qux"}

        node1 = Dict()
        node2 = Dict(min=3)
        node3 = Dict(max=3)
        node4 = Dict(min=3, max=3)
        node5 = Dict(required=["foo", "bar"])
        node6 = Dict({
            "foo": Integer(),
            "bar": Boolean(),
            "baz": String()
        }, required=["foo"])
        node7 = Dict({
            "foo": String(),
            String(): Boolean()
        })
        node8 = Dict({
            Option("bar", "baz"): Float(),
            "foo": Boolean()
        })
        with self.assertRaisesRegexp(ValidatorNodeError, "must declared once"):
            Dict({
                String(): Pass(),
                Integer(): Pass()
            })
        with self.assertRaisesRegexp(ValidatorNodeError, "must be one of following types:"):
            Dict({
                List(): Pass()
            })
        
        node1check = node1.check(some_dict)
        self.assertEqual(len(node1check), 3)
        self.assertEqual(node1check["foo"], 1.2)
        self.assertEqual(node1check["bar"], True)
        self.assertEqual(node1check["baz"], "qux")
        with self.assertRaises(ValidatorConvertError):
            node1.check("foo")

        self.assertEqual(len(node2.check(some_dict)), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node2.check({"a": 1, "b": 2})
        
        self.assertEqual(len(node3.check(some_dict)), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node3.check({"a": 1, "b": 2, "c": 3, "d": 4})
        
        self.assertEqual(len(node4.check(some_dict)), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "less than 3"):
            node4.check({"a": 1, "b": 2})
        with self.assertRaisesRegexp(ValidatorCheckError, "greater than 3"):
            node4.check({"a": 1, "b": 2, "c": 3, "d": 4})

        self.assertEqual(len(node5.check(some_dict)), 3)
        with self.assertRaisesRegexp(ValidatorCheckError, "required item 'bar' not found"):
            node5.check({"foo": 1, "baz": 3})

        node6check = node6.check(some_dict)
        self.assertEqual(len(node6check), 3)
        self.assertEqual(node6check["foo"], 1)
        self.assertEqual(node6check["bar"], True)
        self.assertEqual(node6check["baz"], "qux")
        with self.assertRaises(ValidatorConvertError):
            node6.check({"foo": "bar"})
        with self.assertRaisesRegexp(ValidatorCheckError, "required item 'foo' not found"):
            node6.check({"bar": False})

        node7check = node7.check({
            "foo": "bar",
            "baz": "on"
        })
        self.assertEqual(node7check["foo"], "bar")
        self.assertEqual(node7check["baz"], True)
        with self.assertRaises(ValidatorConvertError):
            node7.check({1: 2})

        node8check = node8.check({
            "foo": "off",
            "bar": 1.2,
            "baz": 3.4
        })
        self.assertEqual(node8check["foo"], False)
        self.assertEqual(node8check["bar"], 1.2)
        self.assertEqual(node8check["baz"], 3.4)
        with self.assertRaises(ValidatorCheckError):
            node8.check({"bad_key": 1})
        with self.assertRaises(ValidatorConvertError):
            node8.check({"bar": "bad_value"})

    def test_option(self):
        node1 = Option("foo", True, 1)
        node2 = Option("foo", Boolean(), String(), 1, List())

        self.assertEqual(node1.check("foo"), "foo")
        self.assertEqual(node1.check(True), True)
        self.assertEqual(node1.check(1), 1)
        with self.assertRaisesRegexp(ValidatorCheckError, "not contains in options"):
            node1.check("bar")

        self.assertEqual(node2.check("foo"), "foo")
        self.assertEqual(node2.check("bar"), "bar")
        self.assertEqual(node2.check(1), 1)
        self.assertEqual(node2.check("on"), True)
        self.assertEqual(node2.check(["baz"])[0], "baz")
        with self.assertRaisesRegexp(ValidatorCheckError, "not contains in options"):
            node2.check({})
        with self.assertRaisesRegexp(ValidatorCheckError, "not contains in options"):
            node2.check(None)

    def test_pass(self):
        node1 = Pass()
        self.assertEqual(node1.check("foo"), "foo")
        self.assertEqual(node1.check(True), True)
        self.assertEqual(node1.check(1), 1)




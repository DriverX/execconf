import unittest
from execconf.utils import *

class TestUtils(unittest.TestCase):
    def test_recursive_fmt(self):
        self.assertEqual(recursive_fmt("foo %(bar)s baz", {"bar": "BAR"}), "foo BAR baz")
 
        res = recursive_fmt(["foo %(bar)s baz", "%(foo)s %(bar)s baz"], {"bar": "BAR", "foo": "FOO"})
        self.assertEqual(res[0], "foo BAR baz")
        self.assertEqual(res[1], "FOO BAR baz")
 
        res = recursive_fmt(("foo %(bar)s baz", "%(foo)s %(bar)s baz"), {"bar": "BAR", "foo": "FOO"})
        self.assertEqual(res[0], "foo BAR baz")
        self.assertEqual(res[1], "FOO BAR baz")
            
        res = recursive_fmt({"%(foo)s": "%(bar)s baz", "%(bar)s" :"%(foo)s baz"}, {"bar": "BAR", "foo": "FOO"})
        self.assertIn("FOO", res)
        self.assertIn("BAR", res)
        self.assertEqual(res["FOO"], "BAR baz")
        self.assertEqual(res["BAR"], "FOO baz")
            
        self.assertEqual(recursive_fmt(set(["%(foo)s"]), {"foo": "FOO"}), set(["%(foo)s"]))
        self.assertEqual(recursive_fmt(1, {}), 1)
        self.assertEqual(recursive_fmt(1.2, {}), 1.2)
 
        res = recursive_fmt(["foo %(bar)s baz", 123], {"bar": "BAR"})
        self.assertEqual(res[0], "foo BAR baz")
        self.assertEqual(res[1], 123)



import unittest
from execconf import Config
from execconf.utils import frozendict


class TestConfig(unittest.TestCase):
    def test_create(self):
        conf1 = Config({"foo": "bar"})
        conf2 = Config({"foo": ["bar"]})
        conf3 = Config({"foo": {"bar": "baz"}})
        conf4 = Config({"foo": [{"bar": "baz"}]})

        self.assertEqual(conf1.foo, "bar")
        self.assertEqual(conf1["foo"], "bar")
        self.assertTrue(isinstance(conf2.foo, tuple))
        self.assertEqual(conf2.foo[0], "bar")
        self.assertTrue(isinstance(conf3.foo, frozendict))
        self.assertEqual(conf3.foo["bar"], "baz")
        self.assertEqual(conf4["foo"][0]["bar"], "baz")
    
    def test_excepts(self):
        conf1 = Config({"foo": "bar"})
        conf2 = Config({"foo": {"bar": "baz"}})

        with self.assertRaises(AttributeError) as cm:
            conf1.foo = "baz"
        self.assertEqual(cm.exception.message, "Config cannot be modified.")
        self.assertEqual(conf1.foo, "bar")

        with self.assertRaises(AttributeError) as cm:
            del conf1.foo
        self.assertEqual(cm.exception.message, "Config cannot be modified.")
        self.assertEqual(conf1.foo, "bar")
        
        with self.assertRaises(AttributeError) as cm:
            conf1.baz = "qux"
        self.assertEqual(cm.exception.message, "Config cannot be modified.")
        self.assertFalse(hasattr(conf1, "baz"))
        
        with self.assertRaises(AttributeError) as cm:
            conf1["foo"] = "baz"
        self.assertEqual(cm.exception.message, "A Config cannot be modified.")
        self.assertEqual(conf1["foo"], "bar")
        
        with self.assertRaises(AttributeError) as cm:
            conf1["baz"] = "qux"
        self.assertEqual(cm.exception.message, "A Config cannot be modified.")
        self.assertFalse("baz" in conf1)
        
        with self.assertRaises(AttributeError) as cm:
            conf2["foo"]["bar"] = "qux"
        self.assertEqual(cm.exception.message, "A Config cannot be modified.")
        self.assertEqual(conf2.foo["bar"], "baz")



REPLACEMENT = True

EXEC_REPLACEMENT = {"foo": "FOO",
                    "bar": "BAR",
                    "fmt": "%(new_fmt)s"}

FOO = "%(foo)s bar baz"
BAR = "%(foo)s %(bar)s baz"
LIST = ["%(foo)s", "%(bar)s", 123]
ANOTHER_FMT = "%%(some)s"
FMT = "%(fmt)s"



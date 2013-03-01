# Executable config on pure python

## Installation
pip installation
```
pip install execconf
```
or via setup.py
```
python setup.py install
```

## Config example
```python
BOOL_TRUE = True
BOOL_TRUE_INT = 1
BOOL_TRUE_STR1 = "yes"
BOOL_TRUE_STR2 = "true"
BOOL_FALSE = False
BOOL_FALSE_INT = 0
BOOL_FALSE_STR1 = "no"
BOOL_FALSE_STR2 = "false"

STR = "some string"
STR_UNICODE = u"some unicode string"

INT = 123
INT_FLOAT = 123.321

FLOAT = 123.456
FLOAT_INT = 123

LIST = ["foo", "bar", 3]
LIST_TUPLE = ("foo", "bar", 3)

LIST_BOOL = [True, "yes", 1, False, "no", 0]
LIST_INT = [1, 2.3]
LIST_FLOAT = [1, 2.3]
LIST_STR = ["foo", "bar"]

DICT = {
    "BOOL": 1,
    "STR": "some string",
    "INT": 123.456,
    "FLOAT": 123.456
}

OPTION1 = "bar"
OPTION2 = 2

PASS = "ololo"

OTHER = "OTHER"
```

Import and use some package
```python
import os

LOG_PATH = os.path.join("../logs", "some_log.txt")
DEBUG = False
```


## Validation example
```python
BOOL_TRUE = Boolean()
BOOL_TRUE_INT = Boolean()
BOOL_TRUE_STR1 = Boolean()
BOOL_TRUE_STR2 = Boolean()
BOOL_FALSE = Boolean()
BOOL_FALSE_INT = Boolean()
BOOL_FALSE_STR1 = Boolean()
BOOL_FALSE_STR2 = Boolean()

STR = String()
STR_UNICODE = String()

INT = Integer()
INT_FLOAT = Integer()

FLOAT = Float()
FLOAT_INT = Float()

LIST = List()
LIST_TUPLE = List()

LIST_BOOL = ListBoolean()
LIST_INT = ListInteger()
LIST_FLOAT = ListFloat()
LIST_STR = ListString()

DICT = Dict({
    "BOOL": Boolean(),
    "STR": String(),
    "INT": Integer(),
    "FLOAT": Float()
})

OPTION1 = Option("foo", "bar", 2)
OPTION2 = Option("foo", "bar", 2)

PASS = Pass()
```

## Using
```python
from execconf import ConfigLoader

loader = ConfigLoader("./config")
config = loader.load("config.py") # equal - loader.load("config")
```


```python
from execconf import ConfigLoader

loader = ConfigLoader("./config", exts=["ini", "conf"])
config = loader.load("config") # find config.ini or config.conf
```


```python
from execconf import ConfigLoader, ValidatorLoader

validator_loader = ValidatorLoader("./config")
validator = validator_loader.load("validate.py")

config_loader = ConfigLoader("./config", validator=validator)
config = config_loader.load("config.py")
```


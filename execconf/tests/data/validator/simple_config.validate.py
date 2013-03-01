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




FILTER = True

_PRIVATE1 = True
__PRIVATE2 = True

def ignore_def():
    pass

import execconf as ignore_pkg

class IgnoreClass(object):
    pass

IGNORE_INSTANCE = IgnoreClass()

class _IgnoreClass2(dict):
    pass

APPROVE_DICT = _IgnoreClass2()



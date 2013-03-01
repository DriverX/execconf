from utils import frozendict


class Config(frozendict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        
        self.__dict__.update(self)

    def __setattr__(self, k, v):
        raise AttributeError("Config cannot be modified.")

    def __delattr__(self, k):
        raise AttributeError("Config cannot be modified.")




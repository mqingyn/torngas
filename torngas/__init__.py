__author__ = 'mengqingyun'
__version__ = '0.0.8'

version = tuple(map(int, __version__.split('.')))


class Null(object):
    def __new__(cls, *args, **kwargs):
        if '_instance' not in vars(cls):
            cls._instance = super(Null, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs): pass

    def __call__(self, *args, **kwargs): return self

    def __repr__(self): return "Null()"

    def __nonzero__(self): return False

    def __getattr__(self, item): return self

    def __setattr__(self, key, value): return self

    def __delattr__(self, item): return self

    def __len__(self): return 0

    def __iter__(self): return iter(())

    def __getitem__(self, item): return self

    def __delitem__(self, key): return self

    def __setitem__(self, key, value): return self
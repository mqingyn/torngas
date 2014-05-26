#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    utils提供以下工具集
 "Storage", "storage", "storify",
    "Counter", "counter",
    "iters",
    "rstrips", "lstrips", "strips",
    "safeunicode", "safestr", "utf8",
    "TimeoutError", "timelimit",
    "re_compile", "re_subm",
    "group", "uniq", "iterview",
    "IterBetter", "iterbetter",
    "safeiter", "safewrite",
    "dictreverse", "dictfind", "dictfindall", "dictincr", "dictadd",
    "requeue", "restack",
    "listget", "intget", "datestr",
    "numify", "denumify", "commify", "dateify",
    "tryall",
    "autoassign",
    "to36",
"""
from tornado.util import import_object
class LazyImport:
    """lazy import module"""
    def __init__(self,module_name):
        self.module_name=module_name
        self.module=None
    def __getattr__(self,func_name):
        if self.module is None:
            self.module=import_object(self.module_name)
        return getattr(self.module,func_name)

lazyimport=LazyImport

class Null(object):
    def __new__(cls, *args, **kwargs):
        if '_instance' not in vars(cls):
            cls._instance = super(Null, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs): pass

    def __call__(self, *args, **kwargs): return self

    def __repr__(self): return ""

    def __nonzero__(self): return False

    def __getattr__(self, item): return self

    def __setattr__(self, key, value): return self

    def __delattr__(self, item): return self

    def __len__(self): return 0

    def __iter__(self): return iter(())

    def __getitem__(self, item): return self

    def __delitem__(self, key): return self

    def __setitem__(self, key, value): return self

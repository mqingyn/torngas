#-*-coding=utf8-*-
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
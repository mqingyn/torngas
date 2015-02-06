#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from hashlib import md5
from tornado.util import import_object
from tornado.web import ErrorHandler
from torngas.settings_manager import settings
from tornado import gen
from torngas.exception import BaseError
from . import BaseHttpModule

try:
    from tornado.concurrent import is_future
except ImportError:
    from torngas.utils import is_future

EXCLUDE_PREFIX = '!'


class HttpModuleMiddleware(object):
    common_modules = []
    route_modules = {}
    named_handlers = None
    non_executes_modules = {}
    re_complies = {}

    def _execute_module(self, handler, clear, module, method, name=None, **kwargs):
        try:
            def run_method_():
                if method.__name__ == "begin_response":
                    return method(handler, clear, kwargs.pop("chunk", None))
                elif method.__name__ == "begin_render":
                    return method(handler, clear, **kwargs)
                elif method.__name__ == 'begin_request':
                    return method(handler, clear)
                elif method.__name__ == 'complete_response':
                    return method(handler, clear)

            if name:
                if hasattr(handler, 'pattern__'):
                    patt = handler.pattern__

                    if name == patt:
                        url_spec = self.named_handlers.get(name, None)
                        if url_spec:
                            if isinstance(handler, url_spec.handler_class):
                                return run_method_()
                    elif handler.request.re_match_table[name]:
                        return run_method_()

            else:
                pattern__ = getattr(handler, 'pattern__', None)

                def check_(key):
                    non_execute = self.non_executes_modules.get(key, [])
                    if non_execute:
                        for n in non_execute:
                            if isinstance(module, n):
                                return True

                if pattern__ in self.non_executes_modules:
                    if check_(handler.pattern__): return

                if hasattr(handler.request, 're_match_table') and handler.request.re_match_table:
                    for key, match in handler.request.re_match_table.items():
                        if match:
                            if check_(key): return

                if not isinstance(handler, ErrorHandler):
                    return run_method_()

        except BaseException, ex:
            raise

    def _class_wrap(self, handler_class, name, url):
        # 防止使用同一个handler的路由出现错误，pattern__会被相同的handler的被覆盖
        # 用type元类生成一个新的handler_class
        prefix = md5("%s_%s_%s" % (handler_class.__name__, name, url,)).hexdigest()
        new_classname = "%s_%s" % (handler_class.__name__, prefix,)
        wrap_class = type(new_classname,
                          (handler_class,),
                          {
                              '__module__': handler_class.__module__
                          })
        return wrap_class

    def process_init(self, application):
        self.named_handlers = application.named_handlers
        # 为每个载入app的路由设定路由名称

        def check_baseclass_(cls):

            if BaseHttpModule not in cls.__bases__:
                raise BaseError("http_module '%s' must inherit from the \
                Basemodule" % str(cls))

        for k, urlspec in self.named_handlers.items():
            urlspec.handler_class = self._class_wrap(urlspec.handler_class, k, urlspec.repr_pattern)
            urlspec.handler_class.pattern__ = k

        # 通用module载入
        c_modules = settings.COMMON_MODULES
        if c_modules:
            for module in c_modules:
                try:
                    import_m = import_object(module)
                    check_baseclass_(import_m)
                    m = import_m()

                except ImportError:
                    raise
                if m not in self.common_modules:
                    self.common_modules.append(m)
        # 路由级module载入
        r_modules = settings.ROUTE_MODULES
        if r_modules:
            def choice_module_(m):
                if m.startswith("%sall" % EXCLUDE_PREFIX):
                    if c_modules:
                        for cs in self.common_modules:
                            cls_type = cs.__class__
                            if cls_type not in non_modules:
                                non_modules.append(cls_type)

                elif m.startswith(EXCLUDE_PREFIX):
                    import_m = import_object(m.lstrip(EXCLUDE_PREFIX))
                    check_baseclass_(import_m)
                    if import_m not in non_modules:
                        non_modules.append(import_m)
                else:
                    import_m = import_object(m)
                    check_baseclass_(import_m)
                    inst_import_m = import_m()
                    if inst_import_m not in modules_lst:
                        modules_lst.append(inst_import_m)

            for name, r_mods in r_modules.items():
                try:
                    modules_lst = []
                    non_modules = []

                    [choice_module_(m) for m in r_mods]
                    if non_modules:
                        if name not in self.non_executes_modules:
                            self.non_executes_modules[name] = non_modules
                    if name not in self.route_modules:
                        self.route_modules[name] = modules_lst
                    self.re_complies[name] = re.compile(name)
                except ImportError:
                    raise

    @gen.coroutine
    def _do_all_execute(self, handler, clear, method_name, **kwargs):

        for c_module in self.common_modules:
            result = self._execute_module(handler, clear, c_module, getattr(c_module, method_name), **kwargs)
            if is_future(result):
                result = yield result
            if result:
                raise gen.Return(1)

        for name, r_module in self.route_modules.items():
            for md in r_module:
                result = self._execute_module(handler, clear, md, getattr(md, method_name), name, **kwargs)
                if is_future(result):
                    result = yield result
                if result:
                    raise gen.Return(1)

    def process_call(self, request, clear):
        re_matchs = {}
        for key, compil in self.re_complies.items():
            re_matchs[key] = compil.search(request.path)

        request.re_match_table = re_matchs

    def process_request(self, handler, clear):
        return self._do_all_execute(handler, clear, 'begin_request')

    def process_response(self, handler, clear, chunk):
        return self._do_all_execute(handler, clear, 'begin_response', chunk=chunk)

    def process_render(self, handler, clear, template_name, **kwargs):
        return self._do_all_execute(handler, clear, 'begin_render', template_name=template_name, **kwargs)

    def process_endcall(self, handler, clear):
        return self._do_all_execute(handler, clear, 'complete_response')
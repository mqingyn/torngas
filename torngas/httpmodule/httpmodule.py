#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-24.

import sys
from tornado.util import import_object
from tornado.web import ErrorHandler
from torngas.settings_manager import settings
from torngas.middleware import BaseMiddleware
from torngas.exception import BaseError
from torngas.httpmodule import BaseHttpModule

EXCLUDE_PREFIX = '!'


class HttpModuleMiddleware(BaseMiddleware):
    common_modules = set()
    route_modules = {}
    named_handlers = None
    non_executes_modules = {}

    def _execute_module(self, handler, module, method, name=None, chunk=None, **kwargs):
        try:
            def run_method_():
                if method.__name__ == "begin_response":
                    method(handler, chunk)
                else:
                    method(handler)

            if name:
                if name == handler.url_name__:
                    url_spec = self.named_handlers[name]

                    if isinstance(handler, url_spec.handler_class):
                        run_method_()
            else:
                url_name = getattr(handler, 'url_name__', None)

                if url_name in self.non_executes_modules:
                    non_execute = self.non_executes_modules[handler.url_name__]

                    for n in non_execute:
                        if isinstance(module, n):
                            return

                if not isinstance(handler, ErrorHandler):
                    run_method_()
        except BaseException:
            if hasattr(module, 'process_exception'):
                module.process_exception(handler, sys.exc_info())
            else:
                raise

    def process_init(self, application):
        self.named_handlers = application.named_handlers
        # 为每个载入app的路由设定路由名称

        def check_baseclass_(cls):
            if BaseHttpModule not in cls.__bases__:
                raise BaseError("http_module '%s' must inherit from the \
                BaseHttpModule" % str(import_m))

        for k, urlspec in self.named_handlers.items():
            urlspec.handler_class.url_name__ = k

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
                self.common_modules.add(m)
        # 路由级module载入
        r_modules = settings.ROUTE_MODULES
        if r_modules:
            for name, r_mods in r_modules.items():
                try:
                    modules_lst = set()
                    non_modules = set()

                    def choice_module_(m):

                        if m.startswith(EXCLUDE_PREFIX):
                            import_m = import_object(m.lstrip(EXCLUDE_PREFIX))
                            check_baseclass_(import_m)
                            non_modules.add(import_m)
                        else:
                            import_m = import_object(m)
                            check_baseclass_(import_m)
                            modules_lst.add(import_m())

                    [choice_module_(m) for m in r_mods]
                    if non_modules:
                        if name not in self.non_executes_modules:
                            self.non_executes_modules[name] = non_modules
                    if name not in self.route_modules:
                        self.route_modules[name] = modules_lst
                except ImportError:
                    raise

    def _do_all_execute(self, handler, method_name, chunk=None, **kwargs):
        for c_module in self.common_modules:
            self._execute_module(handler, c_module, getattr(c_module, method_name), chunk=chunk, **kwargs)

        for name, r_module in self.route_modules.items():
            [self._execute_module(handler, md, getattr(md, method_name), name, chunk=chunk, **kwargs)
             for md in r_module]

    def process_request(self, handler):
        self._do_all_execute(handler, 'begin_request')

    def process_response(self, handler, chunk=None):
        self._do_all_execute(handler, 'begin_response', chunk)

    def process_endcall(self, handler):
        self._do_all_execute(handler, 'complete_response')


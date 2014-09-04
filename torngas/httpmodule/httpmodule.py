#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-24.

import sys
from tornado.util import import_object
from tornado.web import ErrorHandler
from torngas.settings_manager import settings
from torngas.exception import BaseError
from torngas.httpmodule import BaseHttpModule

EXCLUDE_PREFIX = '!'


class HttpModuleMiddleware(object):
    common_modules = []
    route_modules = {}
    named_handlers = None
    non_executes_modules = {}

    def _execute_module(self, handler, module, method, name=None, **kwargs):
        try:
            def run_method_():
                if method.__name__ == "begin_response":
                    chunk = kwargs.pop("chunk__")
                    return method(handler, chunk)
                elif method.__name__ == "begin_render":
                    template_name = kwargs.pop("template_name__")
                    return method(handler, template_name, **kwargs)
                else:
                    return method(handler)

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
                return module.process_exception(handler, sys.exc_info())
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
                if m not in self.common_modules:
                    self.common_modules.append(m)
        # 路由级module载入
        r_modules = settings.ROUTE_MODULES
        if r_modules:
            for name, r_mods in r_modules.items():
                try:
                    modules_lst = []
                    non_modules = []

                    def choice_module_(m):

                        if m.startswith(EXCLUDE_PREFIX):
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

                    [choice_module_(m) for m in r_mods]
                    if non_modules:
                        if name not in self.non_executes_modules:
                            self.non_executes_modules[name] = non_modules
                    if name not in self.route_modules:
                        self.route_modules[name] = modules_lst
                except ImportError:
                    raise

    def _do_all_execute(self, handler, method_name, **kwargs):
        # if not BaseMiddleware._finish:
        for c_module in self.common_modules:
            self._execute_module(handler, c_module, getattr(c_module, method_name), **kwargs)
            # if BaseMiddleware._finish:
            # break
            # if not BaseMiddleware._finish:
        for name, r_module in self.route_modules.items():
            for md in r_module:
                # if BaseMiddleware._finish:
                # break
                self._execute_module(handler, md, getattr(md, method_name), name, **kwargs)

    def process_request(self, handler, clear):
        self._do_all_execute(handler, 'begin_request')

    def process_response(self, handler, chunk, clear):
        self._do_all_execute(handler, 'begin_response', chunk__=chunk)

    def process_render(self, handler, template_name, clear, **kwargs):
        kwargs['template_name__'] = template_name
        self._do_all_execute(handler, 'begin_render', **kwargs)

    def process_endcall(self, handler, clear):
        self._do_all_execute(handler, 'complete_response')


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.

from tornado.util import import_object
from torngas.exception import BaseError
from torngas.settings_manager import settings
from torngas.middleware import BaseMiddleware
import sys


class MiddlewareManager():
    def __init__(self):
        self.request_middleware = []
        self.response_middleware = []
        self.exception_middleware = []
        self.call_middleware = []
        self.endcall_middleware = []
        self.init_middleware = []
        self.load_middleware()

    def run_init_hooks(self, application):
        self.__run_hooks('init', self.init_middleware, application)

    def run_call_hooks(self, request):
        self.__run_hooks('call', self.call_middleware, request)

    def run_endcall_hooks(self, handler):
        self.__run_hooks('endcall', self.endcall_middleware, handler)

    def run_request_hooks(self, handler):
        self.__run_hooks('request', self.request_middleware, handler)

    def run_response_hooks(self, handler, chunk):
        self.__run_hooks('response', self.response_middleware, handler, chunk=chunk)

    def __run_hooks(self, types, middleware_classes, process_object, chunk=None):
        for middleware_class in middleware_classes:
            if types == 'init':
                middleware_class.process_init(process_object)
            try:
                if types == 'request':
                    middleware_class.process_request(process_object)

                elif types == 'response':
                    middleware_class.process_response(process_object, chunk)

                elif types == 'call':
                    middleware_class.process_call(process_object)

                elif types == 'endcall':
                    middleware_class.process_endcall(process_object)

            except BaseException:
                middleware_class.process_exception(process_object, sys.exc_info())

    def load_middleware(self):
        if hasattr(settings, 'MIDDLEWARE_CLASSES') \
                and len(settings.MIDDLEWARE_CLASSES):
            for midd_class in settings.MIDDLEWARE_CLASSES:
                try:
                    cls = import_object(midd_class)

                except ImportError:
                    raise

                try:
                    inst = cls()
                    if not isinstance(inst, BaseMiddleware):
                        raise BaseError(
                            "middleware '%s' must inherit from the BaseMiddleware" % str(midd_class))
                except Exception:
                    raise
                if hasattr(inst, 'process_init'):
                    self.init_middleware.append(inst)

                if hasattr(inst, 'process_request'):
                    self.request_middleware.append(inst)

                if hasattr(inst, 'process_response'):
                    self.response_middleware.append(inst)

                if hasattr(inst, 'process_call'):
                    self.call_middleware.append(inst)

                if hasattr(inst, 'process_endcall'):
                    self.endcall_middleware.append(inst)

        self.response_middleware.reverse()
        self.endcall_middleware.reverse()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.

from tornado.util import import_object
from .exception import BaseError
from .settings_manager import settings
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


class BaseMiddleware(object):
    """
    编写中间件需继承BaseMiddleware并实现其中任何一个方法即可

    """

    def process_init(self, application):
        """
        :param application: 应用程序对象，此方法在tornado启动时执行一次
        """
        pass

    def process_call(self, request):
        """
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        :param request: 请求对象
        """
        pass

    def process_request(self, handler):
        """
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        """
        pass

    def process_exception(self, ex_obj, exception):
        """
        在除了proecss_init方法外其他方法发生异常时调用
        :param ex_obj: 如果在call方法发生异常，则返回request对象，其他方法返回handler对象
        :param exception: 异常栈对象
        """
        raise

    def process_response(self, handler, chunk=None):
        """
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象
        :param chunk : 响应内容
        """
        pass

    def process_endcall(self, handler):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        """
        pass
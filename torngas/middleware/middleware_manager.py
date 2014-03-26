#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.util import import_object
from torngas.utils import lazyimport

settings_module = lazyimport('torngas.helpers.settings_helper')

class MiddlewareManager():
    def __init__(self):
        self.request_middleware = []
        self.response_middleware = []
        self.exception_middleware = []
        self.call_middleware = []
        self.endcall_middleware = []
        self.init_middleware = []
        self.load()

    def run_init_hooks(self, app):
        self.__run_hooks('init', self.init_middleware, app)

    def run_call_hooks(self, request):
        self.__run_hooks('call', self.call_middleware, request)

    def run_endcall_hooks(self, request):
        self.__run_hooks('endcall', self.endcall_middleware, request)

    def run_request_hooks(self, req_handler):
        self.__run_hooks('request', self.request_middleware, req_handler)

    def run_response_hooks(self, req_handler):

        self.__run_hooks('response', self.response_middleware, req_handler)

    def __run_hooks(self, type, middleware_classes, process_object):
        for middleware_class in middleware_classes:
            if (type == 'init'):
                middleware_class.process_init(process_object)
            try:
                if (type == 'request'):
                    middleware_class.process_request(process_object)

                elif (type == 'response'):
                    middleware_class.process_response(process_object)

                elif (type == 'call'):
                    middleware_class.process_call(process_object)

                elif (type == 'endcall'):
                    middleware_class.process_endcall(process_object)

            except Exception, ex:

                if hasattr(middleware_class, 'process_exception'):

                    middleware_class.process_exception(process_object, ex)
                else:
                    raise

    def load(self):
        if hasattr(settings_module.settings, 'MIDDLEWARE_CLASSES') and len(
                settings_module.settings.MIDDLEWARE_CLASSES) > 0:
            for mclass in settings_module.settings.MIDDLEWARE_CLASSES:

                try:
                    cls = import_object(mclass)
                except ImportError, ex:
                    raise

                try:
                    inst = cls()
                except Exception, ex:
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
        :return:None
        """
        pass

    def process_call(self, request):
        """
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        :param request: 请求对象
        :return:
        """
        pass

    def process_request(self, handler):
        """
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        :return:
        """
        pass

    def process_exception(self, req_handler, exception):
        """
        在除了proecss_init方法外其他方法发生异常时调用
        :param req_handler: 如果在call方法发生异常，则返回request对象，其他方法返回handler对象
        :param exception: 异常栈对象
        :return:
        """
        pass

    def process_response(self, handler):
        """
        请求结束后响应时调用，此时还未触发模版呈现
        :param handler: handler对象
        :return:
        """
        pass

    def process_endcall(self, handler):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        :return:
        """
        pass
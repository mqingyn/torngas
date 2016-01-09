#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
中间件可以实现的方法

class MyMiddleware(object):
    编写中间件需实现其中任何一个方法即可
    中间件的执行流程中在请求阶段，process_call,process_request，process_exception按照中间件的声明顺序执行，
    在响应过程中，process_response，process_render和process_endcall则是按声明顺序倒序执行）
    如果希望提前finish请求并终止当前中间件继续执行，在调用finish后需要return True
    :clear: 如果希望接下来的所有中间件流程终止，则在方法头部调用clear()，以清空中间件的执行队列


    def process_init(self, application):
        :param application: 应用程序对象，此方法在tornado启动时执行一次

    def process_call(self, request, clear):
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        您不能在此方法内finish请求
        :param request: 请求对象


    def process_request(self, handler, clear):
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        支持异步

    def process_render(self, handler, clear, template_name, **kwargs):
        此方法在调用render/render_string时发生


    def process_response(self, handler, clear, chunk):
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象

    def process_endcall(self, handler, clear):
        :param handler: handler对象
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
    def process_exception(self,handler, clear, typ, value, tb):
        异常处理
"""
from functools import partial
from tornado.util import import_object
from tornado.log import gen_log
from tornado import gen
from copy import copy

try:
    from tornado.concurrent import is_future
    from collections import deque
except ImportError:
    from ..utils import is_future


class RequestWrapper(object):
    def __init__(self, request):
        request.wrapper = self
        self.request = request

    process_call = property(lambda self: self.request.call_midds)
    process_request = property(lambda self: self.request.request_midds)
    process_render = property(lambda self: self.request.render_midds)
    process_response = property(lambda self: self.request.response_midds)
    process_endcall = property(lambda self: self.request.end_midds)
    process_exception = property(lambda self: self.request.exc_midds)

    @process_call.setter
    def process_call(self, call_list):
        self.request.call_midds = copy(call_list)

    @process_request.setter
    def process_request(self, call_list):
        self.request.request_midds = copy(call_list)

    @process_render.setter
    def process_render(self, call_list):
        self.request.render_midds = copy(call_list)

    @process_response.setter
    def process_response(self, call_list):
        self.request.response_midds = copy(call_list)

    @process_endcall.setter
    def process_endcall(self, call_list):
        self.request.end_midds = copy(call_list)

    @process_exception.setter
    def process_exception(self, call_list):
        self.request.exc_midds = copy(call_list)

    def clear(self):
        self.request.call_midds.clear()
        self.request.request_midds.clear()
        self.request.render_midds.clear()
        self.request.response_midds.clear()
        self.request.end_midds.clear()
        self.request.wrapper = None


class Manager(object):
    def __init__(self):
        self._INIT_LIST = deque()
        self._CALL_LIST = deque()
        self._REQUEST_LIST = deque()
        self._RENDER_LIST = deque()
        self._RESPONSE_LIST = deque()
        self._ENDCALL_LIST = deque()
        self._EXCEPTION_LIST = deque()

    def register(self, name):
        if isinstance(name, (str, unicode,)):
            name = import_object(name)
        obj = name()

        if self._ismd(obj, 'process_init'):
            self._INIT_LIST.append(obj.process_init)
        if self._ismd(obj, 'process_call'):
            self._CALL_LIST.appendleft(obj.process_call)
        if self._ismd(obj, 'process_request'):
            self._REQUEST_LIST.appendleft(obj.process_request)
        if self._ismd(obj, 'process_render'):
            self._RENDER_LIST.append(obj.process_render)

        if self._ismd(obj, 'process_response'):
            self._RESPONSE_LIST.append(obj.process_response)

        if self._ismd(obj, 'process_endcall'):
            self._ENDCALL_LIST.append(obj.process_endcall)

        if self._ismd(obj, 'process_exception'):
            self._EXCEPTION_LIST.appendleft(obj.process_exception)

    def _ismd(self, obj, method_name):
        m = getattr(obj, method_name, None)
        return m and callable(m)

    def register_all(self, names):
        if not names:
            names = ()

        for midd_class in names:
            self.register(midd_class)

    def set_request(self, request):
        r = RequestWrapper(request)
        r.process_call = self._CALL_LIST
        r.process_request = self._REQUEST_LIST
        r.process_render = self._RENDER_LIST
        r.process_response = self._RESPONSE_LIST
        r.process_endcall = self._ENDCALL_LIST
        r.process_exception = self._EXCEPTION_LIST

    def _get_func(self, request, m, func):
        try:
            cls = []
            if hasattr(request, m):
                cls = getattr(request, m)
            if len(cls):
                cls = cls.pop()

                return getattr(cls, func)
        except Exception, ex:
            gen_log.error(ex)

    def execute_next(self, request, call_list, process_object, *args, **kwargs):
        while call_list and len(call_list):
            method = call_list.pop()
            if method and callable(method):
                clear = partial(self.clear_all, request)
                result = method(process_object, clear, *args, **kwargs)
                if result:
                    break
            else:
                break

    @gen.coroutine
    def execute_next_for_async(self, request, call_list, process_object, *args, **kwargs):

        while call_list and len(call_list):
            method = call_list.pop()
            if method and callable(method):
                clear = partial(self.clear_all, request)
                result = method(process_object, clear, *args, **kwargs)
                if is_future(result):
                    result = yield result
                if result:
                    break
            else:
                break

    def clear_all(self, request):
        request.wrapper.clear()

    def run_init(self, application):
        for func in self._INIT_LIST:
            if callable(func):
                func(application)

    def run_call(self, request):
        return self.execute_next(request, request.wrapper.process_call, request)

    def run_request(self, handler):
        if handler.request.request_midds:
            return self.execute_next_for_async(handler.request, handler.request.wrapper.process_request, handler)

    def run_render(self, handler, template=None, **kwargs):
        return self.execute_next(handler.request, handler.request.wrapper.process_render, handler, template, **kwargs)

    def run_response(self, handler, chunk):
        return self.execute_next(handler.request, handler.request.wrapper.process_response, handler, chunk)

    def run_endcall(self, handler):
        return self.execute_next(handler.request, handler.request.wrapper.process_endcall, handler)

    def run_exception(self, handler, typ, value, tb):
        if self._EXCEPTION_LIST:
            self.execute_next(handler.request, handler.request.wrapper.process_exception, handler, typ, value, tb)
            return True

    def catch_middleware_exc(self, middle_result):
        if middle_result:
            exc_info = middle_result.exc_info()
            if exc_info:
                raise exc_info[1]

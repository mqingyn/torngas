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
except ImportError:
    from ..utils import is_future

_INIT_LIST, _CALL_LIST, _REQUEST_LIST, _RENDER_LIST = [], [], [], []
_RESPONSE_LIST, _ENDCALL_LIST, _EXCEPTION_LIST, = [], [], []
_TINIT, _TCALL, _TREQ, _TREN, _TRES, _TEND, _TEXC = 1, 2, 3, 4, 5, 6, 7
_TYPES = (_TINIT, _TCALL, _TREQ, _TREN, _TRES, _TEND, _TEXC)


class Manager(object):
    _call_object = None
    _call_mapper = {
        _TCALL: ('call_midds', 'process_call',),
        _TREQ: ('request_midds', 'process_request',),
        _TREN: ('render_midds', 'process_render',),
        _TRES: ('response_midds', 'process_response',),
        _TEND: ('end_midds', 'process_endcall',),
        _TEXC: ('exc_midds', 'process_exception',)
    }

    def register(self, name):
        if isinstance(name, (str, unicode,)):
            name = import_object(name)
        name = name()

        if hasattr(name, 'process_init'):
            _INIT_LIST.append(name)
        if hasattr(name, 'process_call'):
            _CALL_LIST.insert(0, name)
        if hasattr(name, 'process_request'):
            _REQUEST_LIST.insert(0, name)
        if hasattr(name, 'process_render'):
            _RENDER_LIST.append(name)

        if hasattr(name, 'process_response'):
            _RESPONSE_LIST.append(name)

        if hasattr(name, 'process_endcall'):
            _ENDCALL_LIST.append(name)

        if hasattr(name, 'process_exception'):
            _EXCEPTION_LIST.insert(0, name)

    def register_all(self, names):
        if not names:
            names = ()

        for midd_class in names:
            self.register(midd_class)

    def set_request(self, request):
        request.call_midds = copy(_CALL_LIST)
        request.request_midds = copy(_REQUEST_LIST)
        request.render_midds = copy(_RENDER_LIST)
        request.response_midds = copy(_RESPONSE_LIST)
        request.end_midds = copy(_ENDCALL_LIST)
        request.exc_midds = copy(_EXCEPTION_LIST)

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

    @gen.coroutine
    def execute_next(self, request, types, process_object, *args, **kwargs):

        midd = self._call_mapper.get(types, None)

        if midd:
            while 1:
                method = self._get_func(request, midd[0], midd[1])

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
        request.call_midds = []
        request.request_midds = []
        request.render_midds = []
        request.response_midds = []
        request.end_midds = []

    def run_init(self, application):
        for func in _INIT_LIST:
            if callable(func.process_init):
                func.process_init(application)

    def run_call(self, request):
        return self.execute_next(request, _TCALL, request)

    def run_request(self, handler):
        return self.execute_next(handler.request, _TREQ, handler)

    def run_render(self, handler, template=None, **kwargs):
        return self.execute_next(handler.request, _TREN, handler, template, **kwargs)

    def run_response(self, handler, chunk):
        return self.execute_next(handler.request, _TRES, handler, chunk)

    def run_endcall(self, handler):
        return self.execute_next(handler.request, _TEND, handler)

    def run_exception(self, handler, typ, value, tb):
        if _EXCEPTION_LIST:
            self.execute_next(handler.request, _TEXC, handler, typ, value, tb)
            return True

    def catch_middleware_exc(self, middle_result):
        exc_info = middle_result.exc_info()
        if exc_info:
            raise exc_info[1]



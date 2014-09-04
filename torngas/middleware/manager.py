#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
from functools import partial
from tornado.util import import_object
from tornado import gen

try:
    from tornado.concurrent import is_future
except ImportError:
    from torngas.utils import is_future
    
from tornado.log import gen_log
import sys
import copy


_INIT_LIST = []
_CALL_LIST = []
_REQUEST_LIST = []
_RENDER_LIST = []
_RESPONSE_LIST = []
_ENDCALL_LIST = []
_EXCEPTION_LIST = []
_TINIT = 0x01
_TCALL = 0x02
_TREQ = 0x03
_TREN = 0x04
_TRES = 0x05
_TEND = 0x06
_TEXC = 0x07
_TYPES = (_TINIT, _TCALL, _TREQ, _TREN, _TRES, _TEND, _TEXC)


class Manager(object):
    _call_object = None

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
            _EXCEPTION_LIST.append(name)


    def register_all(self, names):
        if not names:
            names = ()

        for midd_class in names:
            self.register(midd_class)

    def set_request(self, request):
        c = copy.copy
        request.call_midds = c(_CALL_LIST)
        request.request_midds = c(_REQUEST_LIST)
        request.render_midds = c(_RENDER_LIST)
        request.response_midds = c(_RESPONSE_LIST)
        request.end_midds = c(_ENDCALL_LIST)
        request.exc_midds = c(_EXCEPTION_LIST)

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
        midd = None

        if types == _TCALL:
            midd = ('call_midds', 'process_call',)
        elif types == _TREQ:
            midd = ('request_midds', 'process_request',)
        elif types == _TREN:
            midd = ('render_midds', 'process_render',)
        elif types == _TRES:
            midd = ('response_midds', 'process_response',)
        elif types == _TEND:
            midd = ('end_midds', 'process_endcall',)
        elif types == _TEXC:
            midd = ('exc_midds', 'process_exception',)
        if midd:
            method = self._get_func(request, midd[0], midd[1])
            if method and callable(method):

                clear = partial(self.clear_all, request)

                try:
                    result = method(process_object, clear, *args, **kwargs)
                    if is_future(result):
                        result = yield result
                    if not result:
                        self.execute_next(
                            request, types, process_object,
                            *args, **kwargs)

                except BaseException, ex:
                    process_object.log_exception(*sys.exc_info())

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
        self.execute_next(request, _TCALL, request)

    def run_request(self, handler):

        result = self.execute_next(handler.request, _TREQ, handler)

    def run_render(self, handler, template=None, **kwargs):

        result = self.execute_next(handler.request, _TREN, handler, template, **kwargs)

    def run_response(self, handler, chunk):
        result = self.execute_next(handler.request, _TRES, handler, chunk)

    def run_endcall(self, handler):
        result = self.execute_next(handler.request, _TEND, handler)

    def run_exception(self, handler, typ, value, tb):
        if _EXCEPTION_LIST:
            self.execute_next(handler.request, _TEXC, handler, typ, value, tb)
            return True



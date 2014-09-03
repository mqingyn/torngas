#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
from functools import partial
from tornado.util import import_object
from torngas.exception import BaseError
from torngas.settings_manager import settings
from torngas.middleware import BaseMiddleware
import sys
import copy


_INIT_LIST = []
_CALL_LIST = []
_REQUEST_LIST = []
_RENDER_LIST = []
_RESPONSE_LIST = []
_ENDCALL_LIST = []
_TINIT = 0x01
_TCALL = 0x02
_TREQ = 0x03
_TREN = 0x04
_TRES = 0x05
_TEND = 0x06
_TYPES = (_TINIT, _TCALL, _TREQ, _TREN, _TRES, _TEND,)


class Manager(object):
    _call_object = None

    def use(self, name):
        if isinstance(name, (str, unicode,)):
            name = import_object(name)
        name = name()
        if not isinstance(name, BaseMiddleware):
            raise BaseError(
                "middleware '%s' must inherit from the BaseMiddleware" % str(name))

        if hasattr(name, 'process_init'):
            _INIT_LIST.append(name)

        if hasattr(name, 'process_request'):
            _REQUEST_LIST.append(name)

        if hasattr(name, 'process_response'):
            _RESPONSE_LIST.append(name)

        if hasattr(name, 'process_call'):
            _CALL_LIST.append(name)

        if hasattr(name, 'process_endcall'):
            _ENDCALL_LIST.append(name)

        if hasattr(name, 'process_render'):
            _RENDER_LIST.append(name)

    def use_all(self, names):
        if not names:
            names = ()
        names = set(names)
        for midd_class in names:
            self.use(midd_class)

    def load(self, settings=None):
        if settings:
            self.use_all(settings)

        _RESPONSE_LIST and _RESPONSE_LIST.reverse()
        _ENDCALL_LIST and _ENDCALL_LIST.reverse()


    def set_request(self, request):
        c = copy.copy
        request.call_midd = c(_CALL_LIST)
        request.request_midd = c(_REQUEST_LIST)
        request.render_midd = c(_RENDER_LIST)
        request.response_midd = c(_RESPONSE_LIST)
        request.end_midd = c(_ENDCALL_LIST)

    def _get(self, request, m, func):
        try:
            cls = getattr(request, m)
            if len(cls):
                cls = cls.pop()
                return getattr(cls, func)
        except Exception, ex:
            pass

    def next(self, request, types, process_object, *args, **kwargs):
        midd = None

        if types == _TCALL:
            midd = ('call_midd', 'process_call',)
        elif types == _TREQ:
            midd = ('request_midd', 'process_request',)
        elif types == _TREN:
            midd = ('render_midd', 'process_render',)
        elif types == _TRES:
            midd = ('response_midd', 'process_response',)
        elif types == _TEND:
            midd = ('end_midd', 'process_endcall',)
        if midd:
            method = self._get(request, midd[0], midd[1])
            if method and callable(method):
                next_func = partial(self.next, request, types, process_object, *args,
                                    **kwargs)
                finish_func = partial(self.finish, request)
                try:
                    method(process_object, next=next_func, finish=finish_func, *args, **kwargs)
                except BaseException, ex:
                    execp = self._get(request, midd[0], 'process_exception')
                    if execp and callable(execp):
                        execp(process_object, sys.exc_info(),
                              next=next_func, finish=finish_func)

    def finish(self, req, func=None, go=False, *args, **kwargs):
        if not go:
            req.call_midd = []
            req.request_midd = []
            req.render_midd = []
            req.response_midd = []
            req.end_midd = []
        if func:
            func(*args, **kwargs)

    def run_init(self, application):
        for func in _INIT_LIST:
            if callable(func.process_init):
                func.process_init(application)


    def run_call(self, request):
        self.next(request, _TCALL, request)

    def run_request(self, handler):
        self.next(handler.request, _TREQ, handler)

    def run_render(self, handler, template=None, **kwargs):
        kw = copy.copy(kwargs)
        self.next(handler.request, _TREN, handler, template, **kw)

    def run_response(self, handler, chunk):
        self.next(handler.request, _TRES, handler, chunk)

    def run_endcall(self, handler):
        self.next(handler.request, _TEND, handler)




#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
from functools import partial
from tornado.util import import_object
from torngas.exception import BaseError
from tornado.log import gen_log
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

        for midd_class in names:
            self.use(midd_class)

    def load(self, settings=None):
        if settings:
            self.use_all(settings)
        _INIT_LIST and _INIT_LIST.reverse()
        _CALL_LIST and _CALL_LIST.reverse()
        _REQUEST_LIST and _REQUEST_LIST.reverse()
        _RENDER_LIST and _RENDER_LIST.reverse()

    def set_request(self, request):
        c = copy.copy
        request.call_midds = c(_CALL_LIST)
        request.request_midds = c(_REQUEST_LIST)
        request.render_midds = c(_RENDER_LIST)
        request.response_midds = c(_RESPONSE_LIST)
        request.end_midds = c(_ENDCALL_LIST)

    def _get_func(self, request, m, func):
        try:
            cls = getattr(request, m)
            if len(cls):
                cls = cls.pop()
                return getattr(cls, func)
        except Exception, ex:
            gen_log.error(ex)

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
        if midd:
            method = self._get_func(request, midd[0], midd[1])
            if method and callable(method):
                next_func = partial(self.execute_next, request, types, process_object, *args,
                                    **kwargs)
                finish_func = partial(self.finish, request)
                try:
                    method(process_object, do_next=next_func, finish=finish_func, *args, **kwargs)
                except BaseException, ex:
                    try:
                        method.im_class.process_exception(method.im_self,
                                                          process_object,
                                                          sys.exc_info(),
                                                          do_next=next_func,
                                                          finish=finish_func)
                    except Exception, ex:
                        gen_log.error(ex)

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
        self.execute_next(request, _TCALL, request)

    def run_request(self, handler):
        self.execute_next(handler.request, _TREQ, handler)

    def run_render(self, handler, template=None, **kwargs):
        kw = copy.copy(kwargs)
        self.execute_next(handler.request, _TREN, handler, template, **kw)

    def run_response(self, handler, chunk):
        self.execute_next(handler.request, _TRES, handler, chunk)

    def run_endcall(self, handler):
        self.execute_next(handler.request, _TEND, handler)




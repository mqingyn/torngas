#!/usr/bin/env python
# -*- coding: utf-8  -*-
from torngas.utils import lazyimport
from torngas.middleware import BaseMiddleware

__author__ = 'qingyun.meng'

"""
Description: signal from django
SignalMiddleware提供在程序运行至中间件call,request,response,endcall四个阶段时触发信号的能力

"""
signals_module = lazyimport('torngas.dispatch')


class SignalMiddleware(BaseMiddleware):
    def process_call(self, request, do_next, finish):
        signals_module.signals.call_started.send(sender=request.__class__)
        do_next()

    def process_request(self, handler, do_next, finish):
        signals_module.signals.handler_started.send(sender=handler.__class__)
        do_next()

    def process_response(self, handler, chunk, do_next, finish):
        signals_module.signals.handler_finished.send(sender=handler.__class__)
        do_next()

    def process_endcall(self, handler, do_next, finish):
        signals_module.signals.call_finished.send(sender=handler.__class__)
        do_next()


if __name__ == '__main__':
    pass
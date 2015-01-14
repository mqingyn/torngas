#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
Description: signal from django
SignalMiddleware提供在程序运行至中间件call,request,response,endcall四个阶段时触发信号的能力

"""
from torngas.dispatch import signals


class SignalMiddleware(object):
    def process_call(self, request, clear):
        signals.call_started.send(sender=request.__class__)


    def process_request(self, handler, clear):
        signals.handler_started.send(sender=handler.__class__)


    def process_response(self, handler, clear, chunk):
        signals.handler_finished.send(sender=handler.__class__)


    def process_endcall(self, handler, clear):
        signals.call_finished.send(sender=handler.__class__)


if __name__ == '__main__':
    pass
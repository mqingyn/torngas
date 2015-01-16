#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
中间件可能需要实现的类和方法
"""


class MyMiddleware(object):
    def process_init(self, application):
        """
        :param application: 应用程序对象，此方法在tornado启动时执行一次
        """

    def process_call(self, request, clear):
        """
        在请求request对象创建时，参数为请求对象，此时还未匹配路由handler
        :param request: 请求对象
        """

    def process_request(self, handler, clear):
        """
        匹配路由后，执行处理handler时调用,**支持异步**
        :param handler: handler对象

        """

    def process_render(self, handler, clear, template_name, **kwargs):
        """
        此方法在调用render/render_string时发生
        :param handler: handler对象
        :param template_name: 模板名称
        :param kwargs: 模板参数
        """

    def process_response(self, handler, clear, chunk):
        """
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象
        :param chunk : 响应内容，chunk为携带响内容的list，你不可以直接对chunk赋值，
            可以通过chunk[index]来改写响应内容，或再次执行handler.write()
        """

    def process_endcall(self, handler, clear):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        """

    def process_exception(self, handler, clear, typ, value, tb):
        """
        请求过程引发异常时调用，你可以通过这个方法捕获在请求过程中的未捕获异常
        如果没有中间件实现此方法，则调用tornado RequestHandler.log_exception方法。
        :param handler: handler对象
        :param typ: 等同RequestHandler.log_exception的参数，异常类型值和异常堆栈信息
        :param value:异常值信息
        :param tb:异常堆栈
        """
#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
中间件可能需要实现的类和方法
"""


class MyMiddleware(object):
    """
    编写中间件需实现其中任何一个方法即可
    中间件的执行流程中在请求阶段，call,request按照中间件的声明顺序执行，
    在响应过程中，exception，response，endcall和render则是按声明顺序倒序执行）

    :param do_next: 如果希望中间件继续下一个中间件方法的执行，则必须在结尾调用此方法，一般来说这是必须的
    :clear: 如果希望以下的所有中间件流程终止，则在方法头部调用此方法，以清空中间件的执行队列
            与next不同，clear会导致其余的中间件方法在该请求中**全部失效**，而不调用next()只会导致所有中间件的当前方法失效

    """

    def process_init(self, application):
        """
        :param application: 应用程序对象，此方法在tornado启动时执行一次
        """
        pass

    def process_call(self, request, do_next, clear):
        """
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        您不能在此方法内finish
        :param request: 请求对象
        """
        do_next()

    def process_request(self, handler, do_next, clear):
        """
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        """
        do_next()

    def process_exception(self, handler, typ, value, tb):
        """
        在除了proecss_init方法外其他方法发生异常时调用
        :param ex_obj: 如果在call方法发生异常，则返回request对象，其他方法返回handler对象
        :param exception: 异常栈对象
        """
        pass

    def process_render(self, handler, template_name, do_next, clear, **kwargs):
        """
        此方法在调用render/render_string时发生
        :param handler: handler对象
        :param template_name: 模板名称
        :param kwargs: 模板参数
        """
        do_next()

    def process_response(self, handler, chunk, do_next, clear):
        """
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象
        :param chunk : 响应内容
        """
        do_next()

    def process_endcall(self, handler, do_next):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        """
        do_next()
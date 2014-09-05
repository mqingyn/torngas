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

    def process_call(self, request, clear):
        """
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        您不能在此方法内finish
        :param request: 请求对象
        """


    def process_request(self, handler, clear):
        """
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        支持异步
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
        :param chunk : 响应内容
        """


    def process_endcall(self, handler, clear):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        """


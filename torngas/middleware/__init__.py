#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.


class BaseMiddleware(object):
    """
    编写中间件需继承BaseMiddleware并实现其中任何一个方法即可

    """

    def process_init(self, application):
        """
        :param application: 应用程序对象，此方法在tornado启动时执行一次
        """
        pass

    def process_call(self, request):
        """
        在请求进入application时调用，参数为请求对象，此时还未匹配路由
        :param request: 请求对象
        """
        pass

    def process_request(self, handler):
        """
        匹配路由后，执行处理handler时调用
        :param handler: handler对象
        """
        pass

    def process_exception(self, ex_obj, exception):
        """
        在除了proecss_init方法外其他方法发生异常时调用
        :param ex_obj: 如果在call方法发生异常，则返回request对象，其他方法返回handler对象
        :param exception: 异常栈对象
        """
        raise

    def process_render(self, handler, template_name, **kwargs):
        """
        此方法在调用render/render_string时发生
        :param handler: handler对象
        :param template_name: 模板名称
        :param kwargs: 模板参数
        """
        pass

    def process_response(self, handler, chunk=None):
        """
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象
        :param chunk : 响应内容
        """
        pass

    def process_endcall(self, handler):
        """
        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
        :param handler: handler对象
        """
        pass
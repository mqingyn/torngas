# !/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
class BaseHttpModule(object):
    """
    编写httpmodule需继承BaseHttpModule并实现其中任何一个方法即可

    """
    _instance_lock = threading.Lock()
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            with cls._instance_lock:
                cls.__instance = super(BaseHttpModule, cls).__new__(
                    cls, *args, **kwargs)

        return cls.__instance

    def begin_request(self, handler, clear):
        """
        匹配路由后，执行处理handler时调用,你可以在这里对request进行过滤后finish request
        :param handler: handler对象
        v1.4.2:支持异步
        """
        pass


    def begin_render(self, handler, clear, template_name, **kwargs):
        """

        :param handler: 返回handler对象
        :param template_name: 模板名称
        :param kwargs: 模板变量
        """
        pass

    def begin_response(self, handler, clear, chunk=None):
        """
        请求结束后响应时调用，此事件在finish之前,render之后被调用，
        这里你可以对响应数据做最后的处理
        ***切记，这里不能再次调用finish，否则会发生循环调用导致错误***
        :param handler: handler对象
        """
        pass

    def complete_response(self, handler, clear):
        """
        请求呈现客户端后调用
        :param handler: handler对象
        """
        pass


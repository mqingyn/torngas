#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
线程future
如果某些函数耗时较长，且不提供异步回调的功能，例如同步调用mysql，执行一个耗时命令并返回结果，
这些函数无法利用tornado的async特性，此处利用线程池模拟了一个异步方法，可以防止同步耗时操作阻塞进程，
只要在需要异步的方法上加@async_execute装饰器，并且函数最后一个参数名为callback，则该函数便可以支持
@asynchronous或gen.Task的非阻塞方式调用

依赖：该方法必须安装futures模块才可以使用
例子：
    
class Test(Base):
    @coroutine
    def get(self):
        a=''
        b=''
        #支持使用gen的task模块来同步化异步调用
        result = yield Task(self.dosomething, a, b)
        self.finish(result)

    @async_execute
    def dosomething(self,a,b,callback=None):
        # 这里可能耗时很久
        #callback参数不会在这里有任何调用，这个耗时方法本身并没有异步，
        #同步的方法无论如何都不会毫无代价的变成异步，
        #该装饰器为此模拟了异步操作，但注意：这是用线程池模拟的
        # something...
        result='return'
        return result

class Test(Base):
    @asynchronous
    def get(self):
        a=''
        b=''
        #这是用tornado标准的异步回调方式
        self.dosomething(a,b,self.callback)

    def callback(self,result):
        #回调函数
        self.finish(result)

    @async_execute
    def dosomething(self,a,b,callback=None):
        #耗时操作
        result='return'
        return result
"""

import functools
from tornado.netutil import Resolver, ThreadedResolver
from tornado.ioloop import IOLoop

Resolver.configure('tornado.netutil.ThreadedResolver',
                   num_threads=10)

from torngas.exception import ArgumentError


def async_execute(method):
    @functools.wraps(method)
    def decor(*args, **kwargs):
        def wrapper(callback):
            thread_resolver = ThreadedResolver()
            fut = thread_resolver.executor.submit(method, *args, **kwargs)
            fut.add_done_callback(
                lambda future: IOLoop.current().add_callback(functools.partial(callback, future.result())))

        callback = kwargs.get('callback', None)

        if not callback:
            callback = args[-1]
        if not callable(callback):
            raise ArgumentError("The last parameter named 'callback' must be a callable function.")

        return wrapper(callback)

    return decor


if __name__ == '__main__':
    pass

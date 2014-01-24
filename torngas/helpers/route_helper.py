#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas import exception
from tornado.web import url as urlspec
from tornado.util import import_object


class RouteLoader(object):
    """
    路由加载器，将路由加载进tornado的路由系统中
    path:由于设计为子应用形式，路由最终路径为 /path/你的路由，比如blog应用下的/index,会被解析为/blog/index,
        如果不希望在路由前加/path，则为单个路由设置path='/'，path为必填参数
    app_name:设置为子应用的模块名，大小写必须相同，必填
    """

    def __init__(self, path=None, subapp_name=None):
        if not path:
            raise exception.UrlError('path arg not found!')
        if not subapp_name:
            raise exception.UrlError('app_name arg not found!')
        self.path = path if path != '/' else ''
        self.subapp_name = subapp_name

    def urlhelper(self, *urllist):
        """
        路由列表list
        """
        urls = []
        for u in urllist:
            handler_module = '.'.join([self.subapp_name, u.get('handler_module', '')])
            pattern = u.get('pattern')
            pattern += '?' if pattern.endswith('/') else '/?'
            path = u.get('path', None)

            if path:
                if path != '/':
                    pattern = path + pattern
            else:
                pattern = self.path + pattern

            kw = dict(u.get('kwargs', {}))
            kw['subapp_name'] = self.subapp_name
            url_name = ''.join([self.subapp_name, '-', u.get('name')])

            url=urlspec(pattern, import_object(handler_module), kwargs=kw, name=url_name)
            urls.append(url)

        return urls


class url(object):
    """

    :param name:路由的名字，设计为必填项。这样能更好的管理路由，方便使用reverse_url生成路由
    :param pattern:路由表达式
    :param process_setting:路由的handler，view，path设置
    :param kwargs:额外参数提供
    :return:dict，路由字典
    """

    def __call__(self, name=None, pattern=None, handler_module='', path=None, kwargs=None):
        if not kwargs:
            kwargs = {}
        return dict(
            pattern=pattern,
            handler_module=handler_module,
            name=name,
            path=path,
            kwargs=kwargs
        )


url = url()


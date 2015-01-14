# !/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
from tornado.web import url as urlspec
from tornado.util import import_object
from torngas.exception import UrlError


class Url(object):
    overall_kw = None
    prefix = None

    def __init__(self, prefix=None, **kwargs):
        self.prefix = prefix

        if kwargs:
            self.overall_kw = kwargs

    def __call__(self, pattern, handler, kwargs=None, name=None):
        kw = {}
        if self.overall_kw:
            kw.update(self.overall_kw)
        if kwargs:
            kw.update(kwargs)

        if self.prefix and isinstance(handler, str):
            handler = "%s.%s" % (self.prefix, handler)

        urlsp = urlspec(pattern,
                        handler,
                        kwargs=kw,
                        name=name)
        urlsp.repr_pattern = pattern
        return urlsp


def route(*pattens):
    urls = []
    for patt in pattens:
        if isinstance(patt, (tuple, list)):
            urls += list(patt)
        else:
            urls.append(patt)
    return urls


def include(pattern, handlers, prefix_name=None):
    """
    当你有多组url分布在不同的文件，或者你有多组url前缀不同,include可以帮你组织路由
    eg:
    url1.py:
        url=Url('handler_abc')
        URLS = route(
            url(r'/add/','add.AddHandler'),
            ...
        )
    url2.py:
        url=Url()
        URLS = route(
            url(r'/list/','handler_efg.list.ListHandler'),
            ...,
            include('/admin','url1.URLS')
        )

    最终的url可能类似于这样：
    url = [
        r'/list/','handler_efg.list.ListHandler',
        ...,
        r'/admin/add/' , 'handler_abc.add.AddHandler',
        ...

    ]
    app = Application(url)
    """
    try:
        if prefix_name:
            new_name = '%s-%s' % (prefix_name, '%s')
        else:
            new_name = '%s'
        if handlers and isinstance(handlers, str):
            handlers = import_object(handlers)
        else:
            handlers = handlers
        urlspecs = []
        if not pattern.endswith('/'):
            pattern += '/'

        if handlers and isinstance(handlers, (tuple, list)):
            for handler in handlers:
                if handler and isinstance(handler, urlspec):
                    patt = pattern + handler.repr_pattern \
                        .lstrip('^').lstrip('//').lstrip('/')
                    urlsp = urlspec(patt,
                                    handler.handler_class,
                                    kwargs=handler.kwargs,
                                    name=new_name % handler.name
                                    if handler.name else handler.name)

                    urlsp.repr_pattern = patt
                    urlspecs.append(urlsp)
            return urlspecs
        else:
            raise UrlError('url error,it is must be an tuple or list')
    except Exception:
        raise
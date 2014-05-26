#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
import warnings
from tornado.web import url as urlspec
from tornado.util import import_object
from exception import UrlError


class Url(object):
    overall_kw = None
    prefix = None

    def __init__(self, prefix=None, **kwargs):
        self.prefix = prefix

        if kwargs:
            self.overall_kw = kwargs

    def __call__(self, pattern='', handler='', kwargs=None, name=None):
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

    def route(self, *pattens):
        urls = []
        for patt in pattens:
            if isinstance(patt, (tuple, list)):
                urls += list(patt)
            else:
                urls.append(patt)
        return urls


def include(pattern, handlers, prefix_name=None):
    try:
        if prefix_name:
            new_name = '%s-%s' % (prefix_name, '%s')
        else:
            new_name = '%s'
            warnings.warn("you should give a 'prefix_name' for include urls,to avoid naming conflicts")
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
                    urlspecs.append(urlspec(patt,
                                            handler.handler_class,
                                            kwargs=handler.kwargs,
                                            name=new_name % handler.name
                                            if handler.name else handler.name))
            return urlspecs
        else:
            raise UrlError('url error,it is must be an tuple or list')
    except Exception:
        raise
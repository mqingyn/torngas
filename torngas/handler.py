#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common handler,webhandler,apihandler
要获得torngas的中间件等特性需继承这些handler
"""
import json
import tornado.web
from tornado.web import RequestHandler, HTTPError
from torngas.mixins.handler import HandlerMixin
from torngas.mixins.exception import UncaughtExceptionMixin
from torngas.settings_manager import settings
from exception import HttpBadRequestError, Http404


class WebHandler(UncaughtExceptionMixin, HandlerMixin, RequestHandler):
    def create_template_loader(self, template_path):
        loader = self.application.tmpl
        if loader is None:
            return super(WebHandler, self).create_template_loader(template_path)
        else:
            return loader(template_path)


class ApiHandler(HandlerMixin, RequestHandler):
    def get_format(self):
        format = self.get_argument('format', None)
        if not format:
            accept = self.request.headers.get('Accept')
            if accept:
                if 'javascript' in accept.lower():
                    format = 'jsonp'
                else:
                    format = 'json'
        else:
            format = format.lower()
        return format or 'json'

    def write_api(self, obj=None, nofail=False, ensure_ascii=True):
        if not obj:
            obj = {}
        format = self.get_format()
        if format == 'json':
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(obj, ensure_ascii=ensure_ascii))
        elif format == 'jsonp':
            self.set_header("Content-Type", "application/javascript")
            callback = self.get_argument('callback', 'callback')
            self.write('%s(%s);' % (callback, json.dumps(obj, ensure_ascii=ensure_ascii)))
        elif nofail:
            self.write(obj)
        else:
            raise HttpBadRequestError('Unknown response format requested: %s' % format)


class ErrorHandler(UncaughtExceptionMixin, RequestHandler):
    def initialize(self, *args, **kwargs):
        pass

    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise Http404()


if not settings.TORNADO_CONF.get('default_handler_class', None):
    tornado.web.ErrorHandler = ErrorHandler
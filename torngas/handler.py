#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common handler,webhandler,apihandler
要获得torngas的中间件等特性需继承这些handler
"""
import json
from tornado.web import RequestHandler
from mixins.handler import HandlerMixin
from mixins.exception import UncaughtExceptionMixin
from exception import HttpBadRequestError, Http404


class WebHandler(UncaughtExceptionMixin, HandlerMixin, RequestHandler):
    def create_template_loader(self, template_path):
        loader = self.application.tmpl
        if loader is None:
            return super(WebHandler, self).create_template_loader(template_path)
        else:
            return loader(template_path)


class ApiHandler(UncaughtExceptionMixin, HandlerMixin, RequestHandler):
    def get_format(self, params_name="format"):
        format = self.get_argument(params_name, None)
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

    def write_api(self, obj=None, nofail=False, ensure_ascii=True, fmt=None):
        if not obj:
            obj = {}
        if not fmt:
            fmt = self.get_format()

        if fmt == 'json':
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(obj, ensure_ascii=ensure_ascii))
        elif fmt == 'jsonp':
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
"""
common handler,webhandler,apihandler
要获得torngas的中间件等特性需继承这些handler
"""
import json

from tornado.web import RequestHandler, HTTPError
from torngas.mixins.handler import HandlerMixin
from torngas.mixins.exception import UncaughtExceptionMixin


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
                if 'javascript' in accept:
                    format = 'jsonp'
                else:
                    format = 'json'
        return format or 'json'

    def write_api(self, obj=None, nofail=False):
        if not obj:
            obj = {}
        format = self.get_format()
        if format == 'json':
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(obj))
        elif format == 'jsonp':
            self.set_header("Content-Type", "application/javascript")
            callback = self.get_argument('callback', 'callback')
            self.write('%s(%s);' % (callback, json.dumps(obj)))
        elif nofail:
            self.write(json.dumps(obj))
        else:
            raise HTTPError(400, 'Unknown response format requested: %s' % format)


class ErrorHandler(UncaughtExceptionMixin, HandlerMixin, RequestHandler):
    def prepare(self):
        super(ErrorHandler, self).prepare()
        self.set_status(404)
        raise HTTPError(404)
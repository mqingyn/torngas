#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common handler,webhandler,apihandler
要获得torngas的中间件等特性需继承这些handler
"""
import json, functools
import tornado.locale
from tornado.web import RequestHandler
from tornado import stack_context
from settings_manager import settings
from mixins.exception import UncaughtExceptionMixin
from exception import HttpBadRequestError, Http404
from torngas.cache import close_caches
from utils import ThreadlocalLikeRequestContext


class _HandlerPatch(RequestHandler):
    def get_user_locale(self):
        if settings.TRANSLATIONS_CONF.use_accept_language:
            return None

        return tornado.locale.get(settings.TRANSLATIONS_CONF.locale_default)

    def on_finish(self):
        try:
            close_caches()
        except:
            pass

    def _execute(self, transforms, *args, **kwargs):
        current_context = {'request': self.request}

        with stack_context.StackContext(functools.partial(ThreadlocalLikeRequestContext, **current_context)):
            return super(_HandlerPatch, self)._execute(transforms, *args, **kwargs)


class WebHandler(UncaughtExceptionMixin, _HandlerPatch):
    def create_template_loader(self, template_path):
        loader = self.application.tmpl
        if loader is None:
            return super(WebHandler, self).create_template_loader(template_path)
        else:
            return loader(template_path)


class ApiHandler(UncaughtExceptionMixin, _HandlerPatch):
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


class ErrorHandler(UncaughtExceptionMixin, _HandlerPatch):
    def initialize(self, *args, **kwargs):
        pass

    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise Http404()


if settings.MIDDLEWARE_CLASSES:
    from mixins.miiddleware import MiddlewareHandlerMixin

    WebHandler.__bases__ = (MiddlewareHandlerMixin,) + WebHandler.__bases__
    ApiHandler.__bases__ = (MiddlewareHandlerMixin,) + ApiHandler.__bases__

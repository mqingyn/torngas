#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
"""
common handler,webhandler,apihandler
要获得torngas的中间件等特性需继承这些handler
"""
import json
import tornado.locale
from tornado.web import RequestHandler, HTTPError
from logger.client import general_logger
from torngas.settings_manager import settings
from torngas.mixins.exception import UncaughtExceptionMixin


class CommonHandler(RequestHandler):
    _url_kwargs = {}

    def __init__(self, application, request, **kwargs):
        if kwargs:
            self._url_kwargs.update(kwargs)
            kwargs.clear()
        super(CommonHandler, self).__init__(application, request, **kwargs)

    def prepare(self):
        self.application.middleware_manager.run_request(self)
        return self.on_prepare()

    def on_prepare(self):
        pass

    def render_string(self, template_name, **kwargs):
        self.application.middleware_manager.run_render(self, template_name, **kwargs)
        return super(CommonHandler, self).render_string(template_name, **kwargs)

    def finish(self, chunk=None):
        # finish之前可能执行过多次write，反而chunk可能为None
        # 真正的chunk数据在self._write_buffer中，包含历次write的数据
        # 这里将chunk数据write进_write_buffer中，然后将chunk置空
        if chunk:
            self.write(chunk)
            chunk = None
        self.application.middleware_manager.run_response(self, self._write_buffer)
        super(CommonHandler, self).finish(chunk)

    def write(self, chunk, status=None):
        if status:
            self.set_status(status)
        super(CommonHandler, self).write(chunk)

    def log_exception(self, typ, value, tb):
        """重写404请求的异常处理
        """
        if isinstance(value, HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message
                args = ([value.status_code, self._request_summary()] +
                        list(value.args))
                general_logger.warning(format, *args)
        else:
            general_logger.error("Uncaught exception %s\n%r", self._request_summary(),
                            self.request, exc_info=(typ, value, tb))

    def on_finish(self):
        self.application.middleware_manager.run_endcall(self)
        self.complete_finish()

    def complete_finish(self):
        pass

    def get_user_locale(self):
        if settings.TRANSLATIONS_CONF.use_accept_language:
            return None

        return tornado.locale.get(settings.TRANSLATIONS_CONF.locale_default)


class WebHandler(UncaughtExceptionMixin, CommonHandler):
    def create_template_loader(self, template_path):
        loader = self.application.tmpl
        if loader is None:
            return super(CommonHandler, self).create_template_loader(template_path)
        else:
            return loader(template_path)


class ApiHandler(CommonHandler):
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


class ErrorHandler(UncaughtExceptionMixin, CommonHandler):
    def prepare(self):
        super(ErrorHandler, self).prepare()
        self.set_status(404)
        raise HTTPError(404)
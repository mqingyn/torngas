#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.

"""
access log中间件，替换tornado的log_request实现插件式日志输出
"""
from datetime import datetime
from torngas.middleware import BaseMiddleware
from torngas.settings_manager import settings
from torngas.logger.client import access_logger


def log_request(handler):
    if settings.ACCESS_LOGGING_OPEN:
        _datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request_time = 1000.0 * handler.request.request_time()
        user_agent = handler.request.headers.get("User-Agent", "-")
        remote_ip = handler.request.remote_ip
        uri = handler.request.uri
        method = handler.request.method
        version = handler.request.version
        status = handler.get_status()
        referer = handler.request.headers.get('Referer', "-")
        content_length = handler._headers.get("Content-Length", "-")
        _message = '%s - - [%s] "%s %s %s" %s %s "%s" "%s" %dms' % (
            remote_ip,
            _datetime,
            method,
            uri,
            version,
            status,
            content_length,
            referer,
            user_agent,
            request_time
        )
        access_logger.info(_message)


class AccessLogMiddleware(BaseMiddleware):
    def process_init(self, application):
        def _(__):
            pass

        application.settings['log_function'] = _

    def process_endcall(self, handler):
        log_request(handler)

    def process_exception(self, ex_obj, exception):
        pass

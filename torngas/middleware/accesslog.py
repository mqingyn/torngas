#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
access log中间件，替换tornado的log_request实现插件式日志输出
"""
from datetime import datetime
import logging

access_log = logging.getLogger('torngas.accesslog')


def log_request(handler):
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
    access_log.info(_message)


class AccessLogMiddleware(object):
    def process_init(self, application):
        application.settings['log_function'] = lambda _: None

    def process_endcall(self, handler, clear):
        log_request(handler)


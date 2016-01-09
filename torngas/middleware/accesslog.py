#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
access log中间件，替换tornado的log_request实现插件式日志输出
"""
from datetime import datetime
import logging

access_log = logging.getLogger('torngas.accesslog')


class AccessLogMiddleware(object):
    def process_init(self, application):
        application.settings['log_function'] = self.log

    def log(self, handler):
        message = '%s - - [%s] "%s %s %s" %s %s "%s" "%s" %dms' % (
            handler.request.remote_ip,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            handler.request.method,
            handler.request.uri,
            handler.request.version,
            handler.get_status(),
            handler.request.headers.get("Content-Length", "-"),
            handler.request.headers.get('Referer', "-"),
            handler.request.headers.get("User-Agent", "-"),
            1000.0 * handler.request.request_time()
        )
        access_log.info(message)

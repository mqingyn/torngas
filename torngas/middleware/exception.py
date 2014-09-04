#!/usr/bin/env python
# -*- coding: utf-8  -*-

__author__ = 'qingyun.meng'

"""
Created by qingyun.meng on 202014/9/4.
Modify by: qingyun.meng
Description: 
"""
from tornado.web import HTTPError
from torngas.logger.client import syslogger


class ExceptionMiddleware(object):
    def process_exception(self, handler, typ, value, tb):
        if isinstance(value, HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message
                args = ([value.status_code, handler._request_summary()] +
                        list(value.args))
                syslogger.warning(format, *args)
        else:
            syslogger.error("Uncaught exception %s\n%r", handler._request_summary(),
                            handler.request, exc_info=(typ, value, tb))

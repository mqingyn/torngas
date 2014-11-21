#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by mengqingyun on 14-5-21.
"""

from tornado.web import HTTPError

try:
    from exceptions import Exception, StandardError, Warning
except ImportError:
    # Python 3
    StandardError = Exception


class BaseError(StandardError):
    """Base Error"""


class ArgumentError(BaseError):
    """Arguments error"""


class ConfigError(BaseError):
    """raise config error"""


class UrlError(BaseError):
    """route write error"""


class Http404(HTTPError):
    def __init__(self, log_message='not found', *args, **kwargs):
        super(Http404, self).__init__(404, log_message, *args, **kwargs)


class HttpForbiddenError(HTTPError):
    def __init__(self, log_message='forbidden', *args, **kwargs):
        super(HttpForbiddenError, self).__init__(403, log_message, *args, **kwargs)


class HttpNotAllowError(HTTPError):
    def __init__(self, log_message='method not allowed', *args, **kwargs):
        super(HttpNotAllowError, self).__init__(405, log_message, *args, **kwargs)


class HttpBadRequestError(HTTPError):
    def __init__(self, log_message='bad request', *args, **kwargs):
        super(HttpBadRequestError, self).__init__(400, log_message, *args, **kwargs)


class Http500(HTTPError):
    def __init__(self, log_message='server error', *args, **kwargs):
        super(Http500, self).__init__(500, log_message, *args, **kwargs)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
torngas exception module
"""
try:
    from exceptions import Exception, StandardError, Warning
except ImportError:
    # Python 3
    StandardError = Exception


class TorngasError(StandardError):
    """Exception related to operation with torngas."""


class ArgumentError(TorngasError):
    """Arguments error"""


class ConfigError(TorngasError):
    """raise config error"""


class UrlError(TorngasError):
    """route write error"""


from tornado.web import HTTPError


class APIError(HTTPError):
    """API error handling exception
    """

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        super(APIError, self).__init__(status_code, log_message, *args, **kwargs)


class Http404(HTTPError):
    def __init__(self, log_message='not found', handler=None, *args, **kwargs):
        if handler:
            handler.set_status(404)
        super(Http404, self).__init__(404, log_message, *args, **kwargs)


class HttpForbiddenError(HTTPError):
    def __init__(self, log_message='forbidden', handler=None, *args, **kwargs):
        if handler:
            handler.set_status(403)
        super(HttpForbiddenError, self).__init__(403, log_message, *args, **kwargs)


class HttpNotAllowError(HTTPError):
    def __init__(self, log_message='method not allowed', handler=None, *args, **kwargs):
        if handler:
            handler.set_status(405)
        super(HttpNotAllowError, self).__init__(405, log_message, *args, **kwargs)


class HttpBadRequestError(HTTPError):
    def __init__(self, log_message='bad request', handler=None, *args, **kwargs):
        if handler:
            handler.set_status(400)
        super(HttpBadRequestError, self).__init__(400, log_message, *args, **kwargs)


class Http500(HTTPError):
    def __init__(self, log_message='server error', handler=None, *args, **kwargs):
        if handler:
            handler.set_status(500)
        super(Http500, self).__init__(500, log_message, *args, **kwargs)


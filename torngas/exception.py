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
    # def __repr__(self):
    #     return 'Configuration for %s is missing or invalid' % self.args[0]


class UrlError(TorngasError):
    """route write error"""


from tornado.web import HTTPError


class APIError(HTTPError):
    """API error handling exception

    API server always returns formatted JSON to client even there is
    an internal server error.
    """

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        super(APIError, self).__init__(status_code, log_message, *args, **kwargs)



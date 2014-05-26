# -*- coding: utf-8  -*-
#!/usr/local/bin/python

"""
Description:logger server
"""
import logging
import tornado.log
from tornado.log import LogFormatter
from ..settings_manager import settings
from .client import applogger

DEFAULT_FORMAT = '[P %(portno)s][%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'


def patch_define_logging_options(options=None):
    pass


def patch_enable_pretty_logging(logger=None, fmt=None):
    if logger is None:
        return
    if not logger.handlers:
        channel = logging.StreamHandler()
        if fmt:
            channel.setFormatter(LogFormatter(fmt=fmt))
        else:
            channel.setFormatter(LogFormatter())
        logger.addHandler(channel)


def patch_tornado_logger():
    if not settings.TORNADO_CONF['debug']:
        logging.getLogger().handlers = []
        tornado.log.app_log = applogger
        tornado.log.gen_log = applogger
        tornado.log.access_log = applogger
    else:
        patch_enable_pretty_logging(logging.getLogger("tornado"), fmt=DEFAULT_FORMAT)


tornado.log.define_logging_options = patch_define_logging_options
# -*- coding: utf-8  -*-
#!/usr/local/bin/python

"""
Created by:Shunping Jiang <shunping.jiang@autonavi.com>
Description:logger server
"""
import logging
import tornado.log
from ..settings_manager import settings
from tornado.options import options


root_logger = logging.getLogger(settings.LOGGER_CONFIG['root_logger_name'])
root_logger.setLevel(settings.LOGGER_CONFIG['root_level'])


#

def load_stream_logger(logger=None, fmt=None):
    if logger is None:
        return
    if not logger.handlers:
        channel = logging.StreamHandler()
        if fmt:
            channel.setFormatter(tornado.log.LogFormatter(fmt=fmt))
        else:
            channel.setFormatter(tornado.log.LogFormatter(fmt=fmt))
        logger.addHandler(channel)


def init_logger_config():
    if settings.LOGGER_CONFIG.use_tornadolog:
        return

    options.logging = None
    logging.getLogger().handlers = []
    if settings.TORNADO_CONF.debug or options.log_to_stderr:
        load_stream_logger(root_logger, fmt=tornado.log.LogFormatter.DEFAULT_FORMAT)
    from .client import SysLogger

    if not settings.TORNADO_CONF.debug:
        tornado.log.app_log = SysLogger
        tornado.log.gen_log = SysLogger
        tornado.log.access_log = SysLogger

    # tornado.log.enable_pretty_logging(None, root_logger)



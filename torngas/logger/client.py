# -*- coding: utf-8  -*-
# !/usr/local/bin/python
import tornado.log
from functools import partial
from ..settings_manager import settings

if not settings.LOGGER_CONFIG['use_tornadolog']:
    from loggers import LoggerLoader

    LoggerLoader.load_logger()
    access_logger = LoggerLoader.get_logger('torngas.accesslog')
    trace_logger = LoggerLoader.get_logger('torngas.tracelog')
    info_logger = LoggerLoader.get_logger('torngas.infolog')
else:
    import tornado.log

    access_logger = tornado.log.access_log
    trace_logger = tornado.log.app_log
    info_logger = tornado.log.gen_log


class _SysLogger(object):
    @property
    def debug(self):
        """
        logging debug message
        """
        return partial(info_logger.debug)

    @property
    def info(self):
        """
        logging info message
        """
        return partial(info_logger.info)

    @property
    def warning(self):
        """
        logging warn message
        """
        return partial(trace_logger.warning)

    @property
    def error(self):
        """
        logging error message
        """
        return partial(trace_logger.error)

    @property
    def exception(self):
        """
        logging exception message
        """
        return partial(trace_logger.exception)


SysLogger = _SysLogger()
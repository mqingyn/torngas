# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import tornado.log
from functools import partial
from ..settings_manager import settings

ACCESS_LOGNAME = 'torngas.accesslog'
TRACE_LOGNAME = 'torngas.tracelog'
INFO_LOGNAME = 'torngas.infolog'


class _SysLogger(object):
    def __init__(self):
        self.root_logger = logging.getLogger('tornado')
        self.access_logger = logging.getLogger(ACCESS_LOGNAME)
        self.trace_logger = logging.getLogger(TRACE_LOGNAME)
        self.info_logger = logging.getLogger(INFO_LOGNAME)

    def parse_logger(self):
        self.root_logger.setLevel(settings.LOGGER_CONFIG['root_level'])

        if not settings.LOGGER_CONFIG['use_tornadolog']:
            from loggers import LoggerLoader

            LoggerLoader.load_logger()
            self.access_logger = LoggerLoader.get_logger(ACCESS_LOGNAME)
            self.trace_logger = LoggerLoader.get_logger(TRACE_LOGNAME)
            self.info_logger = LoggerLoader.get_logger(INFO_LOGNAME)
        else:
            import tornado.log

            self.access_logger = tornado.log.access_log
            self.trace_logger = tornado.log.app_log
            self.info_logger = tornado.log.gen_log


    @property
    def debug(self):
        """
        logging debug message
        """

        return partial(self.info_logger.debug)

    @property
    def info(self):
        """
        logging info message
        """
        return partial(self.info_logger.info)

    @property
    def warning(self):
        """
        logging warn message
        """
        return partial(self.trace_logger.warning)

    @property
    def error(self):
        """
        logging error message
        """
        return partial(self.trace_logger.error)

    @property
    def exception(self):
        """
        logging exception message
        """
        return partial(self.trace_logger.exception)


SysLogger = _SysLogger()
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from functools import partial
ACCESS_LOGNAME = 'torngas.accesslog'
TRACE_LOGNAME = 'torngas.tracelog'
INFO_LOGNAME = 'torngas.infolog'


class _SysLogger(object):
    def __init__(self):
        self.access_logger = logging.getLogger(ACCESS_LOGNAME)
        self.trace_logger = logging.getLogger(TRACE_LOGNAME)
        self.info_logger = logging.getLogger(INFO_LOGNAME)

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


SysLogger = syslogger = _SysLogger()
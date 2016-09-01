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

    # debug logger
    debug = info_logger.debug
    # info logger
    info = info_logger.info
    # warning logger
    warning = info_logger.warning
    # error logger
    error = general_logger.error
    # exception logger
    exception = general_logger.exception


SysLogger = syslogger = _SysLogger()

# -*- coding: utf-8  -*-
# !/usr/local/bin/python
import logging
from ..settings_manager import settings

root_logger = logging.getLogger('tornado')
root_logger.setLevel(settings.LOGGER_CONFIG['root_level'])
from loggers import UsePortRotatingFileHandler, CustomRotatingFileHandler, LoggerLoader
from client import SysLogger, access_logger, trace_logger, info_logger
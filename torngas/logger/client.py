#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun.
import logging
import logging.handlers
from functools import partial
from tornado.options import options
from torngas.settings_manager import settings
# from torngas.logger.server import GENERAL_LOGGER, ACCESS_LOGGER, INFO_LOGGER


socket_handler = logging.handlers.SocketHandler(
    settings.LOGGER_CONFIG['tcp_logging_host'],
    settings.LOGGER_CONFIG['tcp_logging_port'])
__ROOT_LOGGER = logging.getLogger(settings.LOGGER_CONFIG['root_logger_name'])
__ROOT_LOGGER.setLevel(settings.LOGGER_CONFIG['level'])
__ROOT_LOGGER.addHandler(socket_handler)
# 访问记录
access_logger = logging.getLogger(settings.ACCESS_LOGGING_NAME)
# 通用logger
general_logger = logging.getLogger(settings.GENERAL_LOGGING_NAME)
# info logger
info_logger = logging.getLogger(settings.INFO_LOGGING_NAME)


class _Logger(object):
    @property
    def debug(self):
        '''
        logging debug message
        :param cls:
        :param msg:
        '''
        extra = {"portno": str(options.port)}

        return partial(info_logger.debug, extra=extra)

    @property
    def info(self):
        '''
        logging info message
        :param cls:
        :param msg:
        '''
        extra = {"portno": str(options.port)}
        return partial(info_logger.info, extra=extra)

    @property
    def warning(self):
        '''
        logging warn message
        :param cls:
        :param msg:
        '''
        extra = {"portno": str(options.port)}
        return partial(general_logger.warning, extra=extra)

    @property
    def error(self):
        '''
        logging error message
        :param cls:
        :param msg:
        '''
        extra = {"portno": str(options.port)}
        return partial(general_logger.error, extra=extra)

    @property
    def exception(self):
        '''
        :param cls:
        :param exp:
        '''
        extra = {"portno": str(options.port)}
        return partial(general_logger.exception, extra=extra)


applogger = _Logger()
# -*- coding: utf-8  -*-
# !/usr/local/bin/python

"""
Created by:Shunping Jiang <shunping.jiang@autonavi.com>
Modify by:Qingyun Meng <qingyun.meng@autonavi.com>
Description:重构logger client
"""
import os
import logging
import logging.handlers
from functools import partial
from ..settings_manager import settings

if not settings.TORNADO_CONF['debug']:
    socket_handler = logging.handlers.SocketHandler(
        settings.LOGGER_CONFIG['tcp_logging_host'],
        settings.LOGGER_CONFIG['tcp_logging_port'])
    ROOT_LOGGER = logging.getLogger(settings.LOGGER_CONFIG['root_logger_name'])
    ROOT_LOGGER.setLevel(settings.LOGGER_CONFIG['level'])
    ROOT_LOGGER.addHandler(socket_handler)
# 访问记录
access_logger = logging.getLogger(settings.LOGGER_MODULE['ACCESS_LOG']['NAME'])
# 通用logger
general_logger = logging.getLogger(settings.LOGGER_MODULE['GENERAL_LOG']['NAME'])
# info logger
info_logger = logging.getLogger(settings.LOGGER_MODULE['INFO_LOG']['NAME'])


class _SysLogger(object):
    @property
    def debug(self):
        '''
        logging debug message
        :param cls:
        :param msg:
        '''
        extra = {"pid": str(os.getpid())}

        return partial(info_logger.debug, extra=extra)

    @property
    def info(self):
        '''
        logging info message
        :param cls:
        :param msg:
        '''
        extra = {"pid": str(os.getpid())}
        return partial(info_logger.info, extra=extra)

    @property
    def warning(self):
        '''
        logging warn message
        :param cls:
        :param msg:
        '''
        extra = {"pid": str(os.getpid())}
        return partial(general_logger.warning, extra=extra)

    @property
    def error(self):
        '''
        logging error message
        :param cls:
        :param msg:
        '''
        extra = {"pid": str(os.getpid())}
        return partial(general_logger.error, extra=extra)

    @property
    def exception(self):
        '''
        :param cls:
        :param exp:
        '''
        extra = {"pid": str(os.getpid())}
        return partial(general_logger.exception, extra=extra)


SysLogger = _SysLogger()
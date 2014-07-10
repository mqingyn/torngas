# -*- coding: utf-8  -*-
#!/usr/local/bin/python

"""
Created by:Shunping Jiang <shunping.jiang@autonavi.com>
Description:logger server
"""
import logging
import tornado
from tornado.log import LogFormatter
from ..settings_manager import settings

if settings.TORNADO_CONF['debug']:
    DEFAULT_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
else:
    DEFAULT_FORMAT = '[P %(pid)s][%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
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
    # 對於debug模式僅僅輸出在屏幕上，非debug模式輸出到日志文件，廢棄tornado默認的日誌設定
    logging.getLogger().handlers = []
    if not settings.TORNADO_CONF['debug']:
        tornado.log.app_log = SysLogger
        tornado.log.gen_log = SysLogger
        tornado.log.access_log = SysLogger
        patch_enable_pretty_logging(logging.getLogger("default"))
    else:
        patch_enable_pretty_logging(logging.getLogger("tornado"), fmt=DEFAULT_FORMAT)


tornado.log.define_logging_options = patch_define_logging_options
from .client import SysLogger
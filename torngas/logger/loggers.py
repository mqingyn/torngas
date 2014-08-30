# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
import logging
import threading
import logging.handlers
from tornado.log import LogFormatter
from ..settings_manager import settings
from tornado.util import import_object
from torngas.exception import ConfigError
from tornado.options import options

if settings.TORNADO_CONF['debug']:
    DEFAULT_FORMAT = LogFormatter.DEFAULT_FORMAT
else:
    DEFAULT_FORMAT = '[P %(pid)s][%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'


class BaseServerLogger(object):
    __instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            with cls._instance_lock:
                cls.__instance = super(BaseServerLogger, cls).__new__(
                    cls, *args, **kwargs)

        return cls.__instance


    def init(self, log_name, **kwargs):
        self.log_name = log_name
        self.kwargs = kwargs


    def add_handler(self, handler, level=None):
        if not level:
            level = logging.INFO
        log_logger = self.logger
        log_logger.addHandler(handler)
        log_logger.setLevel(level)

    @property
    def logger(self):
        log_logger = logging.getLogger(self.log_name)
        return log_logger

    def new(self):
        methods = dir(self)
        for method in methods:
            handler = getattr(self, method)
            if method.startswith('handler') and callable(handler):
                h, level = handler()
                if h:
                    self.add_handler(h, level)
        return self.logger


class GeneralLogger(BaseServerLogger):
    def __init__(self):
        GENERAL_LOG = settings.LOGGER_MODULE['GENERAL_LOG']
        log_file = GENERAL_LOG['FILE']
        log_name = GENERAL_LOG['NAME']
        if GENERAL_LOG['USE_PORTNO'] and not settings.LOGGER_CONFIG['use_tcp_server']:
            log_file = log_file + '.%s' % options.port
        rollover_when = GENERAL_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])

        log_backupcount = GENERAL_LOG.get('BUCKUP_COUNT', 30)
        delay = GENERAL_LOG.get('DELAY', False)
        utc = GENERAL_LOG.get('UTC', False)
        interval = GENERAL_LOG.get('INTERVAL', 1)

        self.init(log_name, log_file=log_file,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval
        )

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.kwargs['log_file'],
            when=self.kwargs['rollover_when'],
            backupCount=self.kwargs['log_backupcount'],
            encoding="utf-8",
            delay=self.kwargs['delay'],
            utc=self.kwargs['utc'],
            interval=self.kwargs['interval']
        )
        log_handler.setFormatter(self.kwargs['log_formatter'])
        return log_handler, logging.WARNING


class AccessLogger(BaseServerLogger):
    def __init__(self):
        ACCESS_LOG = settings.LOGGER_MODULE['ACCESS_LOG']
        log_file = ACCESS_LOG['FILE']
        log_name = ACCESS_LOG['NAME']
        if ACCESS_LOG['USE_PORTNO'] and not settings.LOGGER_CONFIG['use_tcp_server']:
            log_file = log_file + '.%s' % options.port
        log_formatter = logging.Formatter('%(message)s')
        rollover_when = ACCESS_LOG['ROLLOVER_WHEN']
        log_backupcount = ACCESS_LOG.get('BUCKUP_COUNT', 20)
        delay = ACCESS_LOG.get('DELAY', False)
        utc = ACCESS_LOG.get('UTC', False)
        interval = ACCESS_LOG.get('INTERVAL', 1)
        self.init(log_name, log_file=log_file,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval
        )

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.kwargs['log_file'],
            when=self.kwargs['rollover_when'],
            backupCount=self.kwargs['log_backupcount'],
            encoding="utf-8",
            delay=self.kwargs['delay'],
            utc=self.kwargs['utc'],
            interval=self.kwargs['interval']
        )
        log_handler.setFormatter(self.kwargs['log_formatter'])
        return log_handler, logging.INFO


class InfoLogger(BaseServerLogger):
    def __init__(self):
        INFO_LOG = settings.LOGGER_MODULE['INFO_LOG']
        log_file = INFO_LOG['FILE']
        log_name = INFO_LOG['NAME']
        if INFO_LOG['USE_PORTNO'] and not settings.LOGGER_CONFIG['use_tcp_server']:
            log_file = log_file + '.%s' % options.port
        rollover_when = INFO_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])

        log_backupcount = INFO_LOG.get('BUCKUP_COUNT', 30)
        delay = INFO_LOG.get('DELAY', False)
        utc = INFO_LOG.get('UTC', False)
        interval = INFO_LOG.get('INTERVAL', 1)
        self.init(log_name, log_file=log_file,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval
        )

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.kwargs['log_file'],
            when=self.kwargs['rollover_when'],
            backupCount=self.kwargs['log_backupcount'],
            encoding="utf-8",
            delay=self.kwargs['delay'],
            utc=self.kwargs['utc'],
            interval=self.kwargs['interval']
        )
        log_handler.setFormatter(self.kwargs['log_formatter'])
        return log_handler, logging.INFO


def load_logger(no_propagate=False):
    custom_logger = settings.LOGGER_MODULE
    loggers = []
    logtostd = options.log_to_stderr
    servermode = options.servermode
    for k, v in custom_logger.items():
        try:
            logger = import_object(v['LOGGER'])
            logger = logger().new()
        except ImportError, ex:
            raise ConfigError('%s not found,please give a module path in customlog setting' % v['LOGGER'])
        if not logtostd:
            if servermode == 'logserver':
                logger.propagate = 0
        loggers.append({
            'name': v['NAME'],
            'open': v['OPEN'],
            'logger': logger

        })
    return loggers

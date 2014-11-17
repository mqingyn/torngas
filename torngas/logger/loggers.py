# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
import os
import logging
import threading
import logging.handlers
from tornado.log import LogFormatter
from ..settings_manager import settings
from tornado.util import import_object
from ..exception import ConfigError
from tornado.options import options

if settings.TORNADO_CONF['debug']:
    DEFAULT_FORMAT = LogFormatter.DEFAULT_FORMAT
else:
    # 这个format会要求带进程号,如果需要兼容老版本format，请注意
    DEFAULT_FORMAT = '[PID %(pid)s][%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'


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


class BaseRotatingFileLogger(BaseServerLogger):
    def __init__(self):
        super(BaseRotatingFileLogger, self).__init__()

    def init(self, log_name, log_file=None, use_portno=None, **kwargs):
        """
        初始化配置
        :param log_name: 日志名
        :param log_file: 文件路径
        :param use_portno: 是否启用区分端口号
        :param kwargs: 参数字典
        :return: None
        """
        dir_name, file_name = os.path.split(log_file)

        if not dir_name:
            root_dir = settings.LOGGER_CONFIG['root_dir']
            log_file = os.path.join(root_dir, file_name)
        if use_portno is None or log_file is None:
            raise ConfigError('param use_portno or log_file not found.')

        if use_portno:
            log_file += '.%s' % options.port

        kwargs['log_file'] = log_file
        super(BaseRotatingFileLogger, self).init(log_name, **kwargs)


class GeneralLogger(BaseRotatingFileLogger):
    def __init__(self):
        super(GeneralLogger, self).__init__()
        GENERAL_LOG = settings.LOGGER_MODULE['GENERAL_LOG']
        log_file = GENERAL_LOG['FILE']
        log_name = GENERAL_LOG['NAME']
        use_portno = GENERAL_LOG['USE_PORTNO']
        rollover_when = GENERAL_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])

        log_backupcount = GENERAL_LOG.get('BUCKUP_COUNT', 30)
        delay = GENERAL_LOG.get('DELAY', False)
        utc = GENERAL_LOG.get('UTC', False)
        interval = GENERAL_LOG.get('INTERVAL', 1)

        self.init(log_name,
                  log_file=log_file,
                  use_portno=use_portno,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval)

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


class AccessLogger(BaseRotatingFileLogger):
    def __init__(self):
        super(AccessLogger, self).__init__()
        ACCESS_LOG = settings.LOGGER_MODULE['ACCESS_LOG']
        log_file = ACCESS_LOG['FILE']
        log_name = ACCESS_LOG['NAME']
        use_portno = ACCESS_LOG['USE_PORTNO']
        log_formatter = logging.Formatter('%(message)s')
        rollover_when = ACCESS_LOG['ROLLOVER_WHEN']
        log_backupcount = ACCESS_LOG.get('BUCKUP_COUNT', 20)
        delay = ACCESS_LOG.get('DELAY', False)
        utc = ACCESS_LOG.get('UTC', False)
        interval = ACCESS_LOG.get('INTERVAL', 1)
        self.init(log_name, log_file=log_file,
                  use_portno=use_portno,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval)

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


class InfoLogger(BaseRotatingFileLogger):
    def __init__(self):
        super(InfoLogger, self).__init__()
        INFO_LOG = settings.LOGGER_MODULE['INFO_LOG']
        log_file = INFO_LOG['FILE']
        log_name = INFO_LOG['NAME']
        use_portno = INFO_LOG['USE_PORTNO']
        rollover_when = INFO_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])

        log_backupcount = INFO_LOG.get('BUCKUP_COUNT', 30)
        delay = INFO_LOG.get('DELAY', False)
        utc = INFO_LOG.get('UTC', False)
        interval = INFO_LOG.get('INTERVAL', 1)
        self.init(log_name, log_file=log_file,
                  use_portno=use_portno,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval)

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


class TornadoLogger(BaseRotatingFileLogger):
    def __init__(self):
        super(TornadoLogger, self).__init__()
        TORNADO_LOG = settings.LOGGER_MODULE['TORNADO_LOG']
        log_file = TORNADO_LOG['FILE']
        log_name = TORNADO_LOG['NAME']
        use_portno = TORNADO_LOG['USE_PORTNO']
        rollover_when = TORNADO_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(color=settings.TORNADO_CONF['debug'])

        log_backupcount = TORNADO_LOG.get('BUCKUP_COUNT', 30)
        delay = TORNADO_LOG.get('DELAY', True)
        utc = TORNADO_LOG.get('UTC', False)
        interval = TORNADO_LOG.get('INTERVAL', 1)

        self.init(log_name,
                  log_file=log_file,
                  use_portno=use_portno,
                  rollover_when=rollover_when,
                  log_formatter=log_formatter,
                  log_backupcount=log_backupcount,
                  delay=delay,
                  utc=utc,
                  interval=interval)

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
        return log_handler, settings.LOGGER_CONFIG['root_level']


def load_logger():
    custom_logger = settings.LOGGER_MODULE
    loggers = []

    for k, v in custom_logger.items():
        try:
            logger = import_object(v['LOGGER'])
            logger = logger().new()
        except ImportError, ex:
            raise ConfigError('%s not found,please give a module path in customlog setting' % v['LOGGER'])
        if not settings.TORNADO_CONF['debug']:
            logger.propagate = 0
            # 新版有个问题，ioloop会自动为rootlogger加一个streamhandler，且行为无法更改，这会导致日志被多次记录
            # 于是，设置logger不向父级传递，避免这个问题。除非debug强制开启log_to_stderr
            # pass
        else:
            if options.log_to_stderr is False:
                logger.propagate = 0
            else:
                logger.propagate = 1
        loggers.append({
            'name': v['NAME'],
            'open': v['OPEN'],
            'logger': logger

        })
    return loggers

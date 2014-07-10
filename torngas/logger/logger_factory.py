# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
import logging
import threading
import logging.handlers
from tornado.log import LogFormatter
from ..settings_manager import settings
from . import DEFAULT_FORMAT, DEFAULT_DATE_FORMAT


class BaseServerLogger(object):
    __instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            with cls._instance_lock:
                cls.__instance = super(BaseServerLogger, cls).__new__(
                    cls, *args, **kwargs)

        return cls.__instance


    def init(self, log_file, log_formatter, log_name, rollover_when):
        self.log_file = log_file
        self.log_formatter = log_formatter
        self.log_name = log_name
        self.rollover_when = rollover_when


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


class AccessLogger(BaseServerLogger):
    def __init__(self):
        ACCESS_LOG = settings.LOGGER_MODULE['ACCESS_LOG']
        log_file = ACCESS_LOG['FILE']
        log_name = ACCESS_LOG['NAME']
        log_formatter = logging.Formatter('%(message)s')
        rollover_when = ACCESS_LOG['ROLLOVER_WHEN']
        self.init(log_file, log_formatter, log_name, rollover_when)

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.rollover_when,
            backupCount=30,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler, logging.INFO


class GeneralLogger(BaseServerLogger):
    def __init__(self):
        GENERAL_LOG = settings.LOGGER_MODULE['GENERAL_LOG']
        log_file = GENERAL_LOG['FILE']
        log_name = GENERAL_LOG['NAME']
        rollover_when = GENERAL_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     datefmt=DEFAULT_DATE_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])
        self.init(log_file, log_formatter, log_name, rollover_when)

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.rollover_when,
            backupCount=20,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler, logging.WARNING


class InfoLogger(BaseServerLogger):
    def __init__(self):
        INFO_LOG = settings.LOGGER_MODULE['INFO_LOG']
        log_file = INFO_LOG['FILE']
        log_name = INFO_LOG['NAME']
        rollover_when = INFO_LOG['ROLLOVER_WHEN']
        log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                     datefmt=DEFAULT_DATE_FORMAT,
                                     color=settings.TORNADO_CONF['debug'])

        self.init(log_file, log_formatter, log_name, rollover_when)

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.rollover_when,
            backupCount=5,
            encoding="utf-8",
            delay=True,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler, logging.INFO

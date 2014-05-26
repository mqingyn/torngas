#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
import logging
import logging.handlers
from tornado.log import LogFormatter
from torngas.settings_manager import settings
from torngas.logger import DEFAULT_FORMAT, DEFAULT_DATE_FORMAT


class BaseServerLogger(object):
    log_file = None
    log_formatter = None
    log_name = None

    def handler_constructor(self):
        raise NotImplementedError

    def get_logger(self, level=logging.INFO):
        log_handler = self.handler_constructor()
        log_logger = logging.getLogger(self.log_name)
        log_logger.addHandler(log_handler)
        log_logger.setLevel(level)

        return log_logger


class AccessLogger(BaseServerLogger):
    def __init__(self):
        self.log_file = settings.ACCESS_LOGGING_FILE
        self.log_name = settings.ACCESS_LOGGING_NAME
        self.log_formatter = logging.Formatter('%(message)s')

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=settings.ACCESS_LOGGING_ROLLOVER_WHEN,
            backupCount=30,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler


class GeneralLogger(BaseServerLogger):
    def __init__(self):
        self.log_file = settings.GENERAL_LOGGING_FILE
        self.log_name = settings.GENERAL_LOGGING_NAME
        self.log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                          datefmt=DEFAULT_DATE_FORMAT,
                                          color=settings.TORNADO_CONF['debug'])

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=settings.GENERAL_LOGGING_ROLLOVER_WHEN,
            backupCount=20,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler


class InfoLogger(BaseServerLogger):
    def __init__(self):
        self.log_file = settings.INFO_LOGGING_FILE
        self.log_name = settings.INFO_LOGGING_NAME
        self.log_formatter = LogFormatter(fmt=DEFAULT_FORMAT,
                                          datefmt=DEFAULT_DATE_FORMAT,
                                          color=settings.TORNADO_CONF['debug'])

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=settings.INFO_LOGGING_ROLLOVER_WHEN,
            backupCount=5,
            encoding="utf-8",
            delay=True,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler

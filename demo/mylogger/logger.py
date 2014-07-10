# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置自定义日志示例，实际需按需配置按需放置
"""
import logging
import logging.handlers
from torngas.logger.logger_factory import BaseServerLogger
from torngas.settings_manager import settings


class CustomLogger(BaseServerLogger):
    def __init__(self):
        LOGGER_CONFIG = settings.LOGGER_MODULE['CUSTOM_LOG']
        log_file = LOGGER_CONFIG['FILE']
        log_name = LOGGER_CONFIG['NAME']
        log_formatter = logging.Formatter('%(message)s')
        rollover_when = LOGGER_CONFIG['ROLLOVER_WHEN']
        self.init(log_file, log_formatter, log_name, rollover_when)

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.rollover_when,
            backupCount=10,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler, logging.INFO

        # 欲定义多个不同level的handler，只需要实现一个以handler开头的方法，并返回两个结果：handler，和level
        # def handler_constructor_for_stream(self):
        # handler = logging.StreamHandler()
        # handler.setFormatter(self.log_formatter)
        # return handler, logging.DEBUG


customlogger = CustomLogger().logger


# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置自定义日志示例，实际需按需配置按需放置
"""
import logging
import logging.handlers
from torngas.logger.loggers import BaseRotatingFileLogger
from torngas.settings_manager import settings


class CustomLogger(BaseRotatingFileLogger):
    def __init__(self):
        super(BaseRotatingFileLogger, self).__init__()
        access_log = settings.LOGGER_MODULE['CUSTOM_LOG']

        self.init(access_log['NAME'], log_file=access_log['FILE'],
                  use_portno=access_log['USE_PORTNO'],
                  rollover_when=access_log['ROLLOVER_WHEN'],
                  log_formatter=logging.Formatter('%(message)s'),
                  log_backupcount=access_log.get('BUCKUP_COUNT', 10),
                  delay=access_log.get('DELAY', False),
                  utc=access_log.get('UTC', False),
                  interval=access_log.get('INTERVAL', 1))

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


customlogger = CustomLogger().logger



# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
from torngas.logger.logger_factory import BaseServerLogger
from torngas.settings_manager import settings


class CustomLogger(BaseServerLogger):

    def __init__(self):
        self.logger_config = settings.CUSTOM_LOGGING_CONFIG['CUSTOM_LOG']
        self.log_file = self.logger_config['FILE']
        self.log_name = self.logger_config['NAME']
        self.log_formatter = logging.Formatter('%(message)s')

    def handler_constructor(self):
        log_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.logger_config['ROLLOVER_WHEN'],
            backupCount=30,
            encoding="utf-8",
            delay=False,
            utc=False
        )
        log_handler.setFormatter(self.log_formatter)
        return log_handler

customlog = CustomLogger().get_logger(level=logging.INFO)

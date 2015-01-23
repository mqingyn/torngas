# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import warnings
import logging.handlers
from tornado.log import LogFormatter
from ..settings_manager import settings
from tornado.util import import_object
from tornado.options import options
from torngas.global_settings import LOGGER
DEFAULT_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'



class CustomRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=20, encoding=None, delay=False, utc=False):
        dir_name, file_name = os.path.split(filename)
        if not dir_name:
            root_dir = settings.LOGGER_CONFIG['root_dir']
            filename = os.path.join(root_dir, file_name)

        super(CustomRotatingFileHandler, self).__init__(filename, when, interval, backupCount, encoding, delay,
                                                        utc)


class UsePortRotatingFileHandler(CustomRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=20, encoding=None, delay=False, utc=False):
        try:
            if options.port:
                filename += '.%s' % options.port
        except:
            pass
        super(UsePortRotatingFileHandler, self).__init__(filename, when, interval, backupCount, encoding, delay,
                                                         utc)


class LoggerLoader(object):
    loggers = {}

    @classmethod
    def load_logger(cls):
        log_config = LOGGER
        if 'LOGGER' in settings:
            log_config.update(settings.LOGGER)

        for k, v in log_config.items():
            is_open = v.get('OPEN')
            logger = logging.getLogger(k)

            if is_open:
                cls.load_handler(logger, v)
                if not settings.DEBUG:
                    logger.propagate = 0
                else:
                    if options.log_to_stderr is False:
                        logger.propagate = 0
                    else:
                        logger.propagate = 1
                cls.loggers[k] = logger
            else:
                logger.disabled = True
                warnings.warn("logger %s is not open or not exist in logging config settings." % k)


    @classmethod
    def get_logger(cls, name):
        if name in cls.loggers:
            return cls.loggers[name]
        else:
            return logging.getLogger(name)


    @classmethod
    def load_handler(cls, logger, log_conf):
        global DEFAULT_FORMAT
        if settings.DEBUG:
            DEFAULT_FORMAT = LogFormatter.DEFAULT_FORMAT

        for handl in log_conf['HANDLERS']:
            module = handl.pop("module", None)
            level = handl.pop("level", None)

            if module:
                handler_module = import_object(module)
                handler = handler_module(**handl)
                log_formatter = LogFormatter(fmt=log_conf.get("FORMATTER", DEFAULT_FORMAT),
                                             color=settings.DEBUG)
                handler.setFormatter(log_formatter)
                if level:
                    handler.setLevel(level)
                logger.addHandler(handler)
                logger.setLevel(log_conf.get("LEVEL", "INFO"))


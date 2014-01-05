#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, logging
from torngas.helpers import settings_helper
from tornado.options import options
from tornado.log import LogFormatter
from datetime import datetime

_NAME_PREFIX = 'torngas'


class logger():
    def __init__(self):

        self.config = settings_helper.settings.LOG_CONFIG
        self.dirpath = self.get_log_dirpath()
        self.load_config()

    def get_log_dirpath(self):
        return os.path.join(os.path.abspath(self.config["path"]), str(datetime.now().date()))

    def get_log_abspath(self, file_prefix=_NAME_PREFIX):
        return os.path.join(self.dirpath, '{0}_port[{1}].log'.format(file_prefix, options.port))

    @property
    def getlogger(self, name_prefix=_NAME_PREFIX):
        rootlogger = logging.getLogger(name_prefix)
        fn, lno, func = rootlogger.findCaller()
        if fn.endswith('.py'):
            file_prefix = os.path.splitext(os.path.split(fn)[1])[0]
        else:
            file_prefix = os.path.split(fn)[1]
        file_path = self.get_log_abspath(file_prefix)
        logger = logging.getLogger(name_prefix + '.' + file_prefix)
        if os.path.exists(self.dirpath) and self.get_log_dirpath() == self.dirpath and \
                os.path.isfile(file_path):
            return logger

        else:
            new_dirpath = self.get_log_dirpath()
            if not os.path.exists(new_dirpath):
                os.makedirs(new_dirpath)
            self.dirpath = new_dirpath
            self.set_handler(logger, file_path)

        return logger


    def set_handler(self, logger=None, file_path=None):
        if not logger:
            logger = logging.getLogger(_NAME_PREFIX)
        if not file_path:
            file_path = self.get_log_abspath()
        logging.getLogger().handlers = []
        logger.setLevel(getattr(logging, options.logging.upper()))
        logger.handlers = []

        if options.log_file_prefix:
            channel = logging.handlers.RotatingFileHandler(
                filename=file_path,
                maxBytes=options.log_file_max_size,
                backupCount=options.log_file_num_backups)

            channel.setFormatter(LogFormatter(color=False))
            logger.addHandler(channel)

        if (options.log_to_stderr or
                (options.log_to_stderr is None and not logger.handlers)):
            channel = logging.StreamHandler()

            channel.setFormatter(LogFormatter())
            logger.addHandler(channel)


    def load_config(self):
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)
        options.log_file_prefix = self.get_log_abspath()
        options.logging = self.config["level"]
        options.log_to_stderr = self.config["log_to_stderr"]
        options.log_file_max_size = self.config["filesize"]
        options.log_file_num_backups = self.config["backup_num"]


logger = logger()

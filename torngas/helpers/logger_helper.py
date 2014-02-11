#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, logging
from torngas.helpers import settings_helper
from tornado.options import options
from tornado.log import LogFormatter
from datetime import datetime

_NAME_PREFIX = 'torngas'


class Logger():
    def __init__(self):
        pass

    def get_log_dirpath(self):
        return os.path.join(os.path.abspath(settings_helper.settings.LOG_CONFIG["path"]), str(datetime.now().date()))

    def get_log_abspath(self, file_prefix='web'):
        return os.path.join(self.get_log_dirpath(),
                            '{0}.{1}.{2}.log'.format(options.log_prefix, file_prefix, options.port))

    @property
    def getlogger(self):
        self.load_config()
        rootlogger = logging.getLogger(_NAME_PREFIX)
        fn, lno, func = rootlogger.findCaller()

        if fn.endswith('.py'):
            file_prefix = os.path.splitext(os.path.split(fn)[1])[0]
        else:
            file_prefix = os.path.split(fn)[1]

        file_path = self.get_log_abspath(file_prefix)
        logger = logging.getLogger('.'.join([_NAME_PREFIX, file_prefix]))
        new_dir_path = self.get_log_dirpath()

        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)

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
        dir_path = self.get_log_dirpath()
        if not os.path.exists( dir_path):
            os.makedirs( dir_path)
        config= settings_helper.settings.LOG_CONFIG
        options.log_file_prefix = self.get_log_abspath()
        options.logging =  config["level"]
        options.log_to_stderr =  config["log_to_stderr"]
        options.log_file_max_size = config["filesize"]
        options.log_file_num_backups =config["backup_num"]


logger = Logger()

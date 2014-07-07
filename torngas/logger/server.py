#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
try:
    import cPickle as pickle
except ImportError:
    import pickle
import logging
import struct
import logging.handlers
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado.gen import coroutine, Task
from tornado.util import import_object
from ..settings_manager import settings
from .logger_factory import GeneralLogger, AccessLogger, InfoLogger
from . import patch_tornado_logger

general_l = GeneralLogger()
access_l = AccessLogger()
info_l = InfoLogger()

GENERAL_LOGGER = general_l.get_logger(level=logging.WARNING)
ACCESS_LOGGER = access_l.get_logger(level=logging.INFO)
INFO_LOGGER = info_l.get_logger(level=logging.INFO)


def load_custom_logger():
    custom_logger = settings.CUSTOM_LOGGING_CONFIG
    loggers = []
    for k, v in custom_logger.items():
        logger = import_object(v['LOGGER'])
        logger.propagate = 0
        loggers.append({
            'name': v['NAME'],
            'open': v['OPEN'],
            'logger': logger

        })
    return loggers


custom_loggers = load_custom_logger()


class LoggingTCPServer(TCPServer):
    @coroutine
    def handle_stream(self, stream, address):
        try:
            while 1:
                chunk = yield Task(stream.read_bytes, 4)
                if len(chunk) < 4:
                    break
                unpack_data = struct.unpack('>L', chunk)
                slen = int(unpack_data[0]) if unpack_data else None
                if slen:
                    chunk = yield Task(stream.read_bytes, slen)
                    while len(chunk) < slen:
                        add_result = yield Task(stream.read_bytes, slen - len(chunk))
                        chunk = chunk + add_result
                    obj = pickle.loads(chunk)
                    record = logging.makeLogRecord(obj)
                    self.handle_log_record(record)
        except Exception, ex:
            logging.exception('logserver except: %s' % ex)
        finally:
            if not stream.closed():
                stream.close()

    def handle_log_record(self, record):
        try:
            name = record.name

            def handle_(setting_name, isopen, thislogger):
                if name == setting_name:
                    if isopen:
                        thislogger.handle(record)
                    return True

            handle_loggers = [
                (settings.GENERAL_LOGGING_NAME,
                 settings.GENERAL_LOGGING_OPEN,
                 GENERAL_LOGGER),

                (settings.ACCESS_LOGGING_NAME,
                 settings.ACCESS_LOGGING_OPEN,
                 ACCESS_LOGGER),

                (settings.INFO_LOGGING_NAME,
                 settings.INFO_LOGGING_OPEN,
                 INFO_LOGGER)
            ]

            for n, op, l in handle_loggers:
                if handle_(n, op, l):
                    break
            else:
                for log in custom_loggers:
                    if handle_(log['name'], log['open'], log['logger']):
                        break
                else:
                    logging.getLogger().handle(record)

        except Exception, ex:
            logging.exception('logserver except: %s' % ex)


def run_logserver():
    GENERAL_LOGGER.propagate = 0
    ACCESS_LOGGER.propagate = 0
    INFO_LOGGER.propagate = 0

    patch_tornado_logger()

    server = LoggingTCPServer()
    server.listen(address=settings.LOGGER_CONFIG['tcp_logging_host'],
                  port=settings.LOGGER_CONFIG['tcp_logging_port'])

    IOLoop.instance().start()

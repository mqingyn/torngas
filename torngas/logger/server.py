#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-23.
"""
log server,可以将多个进程的日志汇总，仅在非debug模式启动有效
"""
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
from . import patch_tornado_logger
from ..exception import ConfigError
from ..logger.logger_factory import *


def load_custom_logger():
    custom_logger = settings.LOGGER_MODULE
    loggers = []
    for k, v in custom_logger.items():
        try:
            logger = import_object(v['LOGGER'])
            logger = logger().new()
        except ImportError, ex:
            raise ConfigError('%s not found,please give a module path in customlog setting' % v['LOGGER'])
        logger.propagate = 0
        loggers.append({
            'name': v['NAME'],
            'open': v['OPEN'],
            'logger': logger

        })
    return loggers


class LoggingTCPServer(TCPServer):
    def __init__(self, io_loop=None, ssl_options=None, max_buffer_size=None, loggers=None):
        self.loggers = loggers
        super(LoggingTCPServer, self).__init__(io_loop, ssl_options, max_buffer_size)

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

            for log in self.loggers:
                if handle_(log['name'], log['open'], log['logger']):
                    break
            else:
                logging.getLogger('default').handle(record)

        except Exception, ex:
            logging.getLogger('default').handle(record)
            logging.exception('logserver except: %s' % ex)



def runserver():
    patch_tornado_logger()
    loggers = load_custom_logger()

    server = LoggingTCPServer(loggers=loggers)
    server.listen(address=settings.LOGGER_CONFIG['tcp_logging_host'],
                  port=settings.LOGGER_CONFIG['tcp_logging_port'])

    IOLoop.instance().start()

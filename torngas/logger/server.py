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
from tornado.gen import coroutine
from loggers import load_logger
from ..settings_manager import settings


class LoggingTCPServer(TCPServer):
    def __init__(self, io_loop=None, ssl_options=None, max_buffer_size=None, loggers=None):
        self.loggers = loggers
        super(LoggingTCPServer, self).__init__(io_loop, ssl_options, max_buffer_size)

    @coroutine
    def handle_stream(self, stream, address):
        try:
            while 1:
                chunk = yield stream.read_bytes(4)
                if len(chunk) < 4:
                    break
                unpack_data = struct.unpack('>L', chunk)
                slen = int(unpack_data[0]) if unpack_data else None
                if slen:
                    chunk = yield stream.read_bytes(slen)
                    while len(chunk) < slen:
                        add_result = yield stream.read_bytes(slen - len(chunk))
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
    loggers = load_logger()

    server = LoggingTCPServer(loggers=loggers)
    server.listen(address=settings.LOGGER_CONFIG['tcp_logging_host'],
                  port=settings.LOGGER_CONFIG['tcp_logging_port'])

    IOLoop.instance().start()
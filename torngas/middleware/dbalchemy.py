#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dbalchemy中间件，加入此中间件可以自动帮助dbalchemy模块处理连接的关闭
"""

from torngas.middleware import BaseMiddleware
from torngas.logger.client import SysLogger
from torngas.db.dbalchemy import sql_connection
from tornado.ioloop import PeriodicCallback

connection = sql_connection.connetion


class DBAlchemyMiddleware(BaseMiddleware):
    def process_init(self, application):
        def ping_db_(conn_, pool_recycle):
            # ping db, 防止数据库失联
            PeriodicCallback(conn_.ping_db, pool_recycle * 1000).start()

        for k, conn in connection.items():
            if 'pool_recycle' in conn.kwargs:
                ping_db_(conn, conn.kwargs['pool_recycle'])
            elif 'sqlalchemy.pool_recycle' in conn.base_conf:
                ping_db_(conn, conn.kwargs['sqlalchemy.pool_recycle'])

    def process_endcall(self, handler):
        for k, conn in connection.items():
            if hasattr(conn, 'remove'):
                callable(conn.remove) and conn.remove()

    def process_exception(self, ex_obj, exception):
        SysLogger.error("dbalchemy middleware error:{0}".format(exception.message))
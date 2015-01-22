#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dbalchemy中间件，加入此中间件可以自动帮助dbalchemy模块处理连接的关闭
"""

from ..db.dbalchemy import Connector
from tornado.ioloop import PeriodicCallback
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool
from ..logger import SysLogger
from ..settings_manager import settings

connection = Connector.conn_pool


def connection_event():
    @event.listens_for(Pool, "checkout")
    def ping_connection(dbapi_connection, connection_record, connection_proxy):
        # 在每次从连接池获取一个连接时，首先测试连接池是否畅通
        # 如果不畅通，则断开重新建立连接，及时防丢
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
        except:
            SysLogger.error('database pool has gone away')
            raise exc.DisconnectionError()
        cursor.close()


def ping_db(conn_, ping_inteval):
    PeriodicCallback(conn_.ping_db, ping_inteval * 1000).start()


class DBAlchemyMiddleware(object):
    def process_init(self, application):

        connection_event()
        # 定时ping数据库，防止mysql go away，定时检测防丢
        interval = settings.PING_DB
        if interval > 0:
            for k, conn in connection.items():
                ping_db(conn, interval)

    def process_endcall(self, handler, clear):
        for k, conn in connection.items():
            if hasattr(conn, 'remove'):
                callable(conn.remove) and conn.remove()


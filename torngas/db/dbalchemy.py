# !/usr/bin/env python
# -*- coding: utf-8 -*-

import random, threading
from tornado.ioloop import PeriodicCallback
from torngas.settings_manager import settings
from torngas.exception import ConfigError
from torngas.utils.storage import storage
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import url


_CONNECTION_TYPE = (
    'master',
    'slave',
)


class BaseModel(object):
    query = None
    __tablename__ = ''

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


def _create_session(engine):
    if not engine:
        return None
    session = sessionmaker(bind=engine)
    return scoped_session(session)


class SqlConnection(object):
    _conn_lock = threading.Lock()

    @property
    def connetion(self):
        if hasattr(SqlConnection, '_conn'):
            return SqlConnection._conn
        else:
            with SqlConnection._conn_lock:
                connection_pool = storage()
                connections = settings.DATABASE_CONNECTION

                config = settings.SQLALCHEMY_CONFIGURATION

                for connection_name, connection_item in connections.items():
                    master = []
                    slaves = []
                    kwargs = connection_item.get('kwargs', {})
                    connections_str = connection_item['connections']

                    for conn in connections_str:
                        dburl = url.URL(drivername=conn['DRIVER']
                                        , username=conn['UID']
                                        , password=conn['PASSWD']
                                        , host=conn['HOST']
                                        , port=conn['PORT']
                                        , database=conn['DATABASE']
                                        , query=conn['QUERY'])

                        if conn['ROLE'] == _CONNECTION_TYPE[0]:
                            master.append(dburl)
                        else:
                            slaves.append(dburl)

                    if not len(master):
                        raise ConfigError('conn:%s ,master connection not found.' % connection_name)
                    try:
                        connection_pool[connection_name] = SQLAlchemy(config, master_url=master[0], slaves_url=slaves,
                                                                      **kwargs)
                    except Exception:
                        raise

                SqlConnection._conn = connection_pool
            return SqlConnection._conn


sql_connection = SqlConnection()


def get_base_model():
    return declarative_base(cls=BaseModel, name='Model')


class SQLAlchemy(object):
    """
    Example::

        db = SQLAlchemy("mysql://user:pass@host:port/db", pool_recycle=3600)

        from sqlalchemy import Column, String

        class User(db.Model):
            username = Column(String(16), unique=True, nullable=False)
            password = Column(String(30), nullable=False)



    """

    def __init__(self, base_conf=None, master_url=None, slaves_url=None, **kwargs):
        if not slaves_url:
            slaves_url = []
        if not base_conf:
            base_conf = {}
        self.engine = engine_from_config(base_conf, prefix='sqlalchemy.', url=master_url, **kwargs)
        self._master_session = _create_session(self.engine)
        self._slaves_session = []
        for slave in slaves_url:
            slave_engine = engine_from_config(base_conf, prefix='sqlalchemy.', url=slave, **kwargs)
            self._slaves_session.append(_create_session(slave_engine))

        if 'pool_recycle' in kwargs:
            # ping db, so that mysql won't goaway
            PeriodicCallback(self._ping_db,
                             kwargs['pool_recycle'] * 1000).start()

            # signals.call_finished.connect(self._remove)  #不在自动处理，通过用户手动决

    def remove(self):
        self._master_session.remove()
        if self._slaves_session:
            for slave in self._slaves_session:
                slave.remove()

    @property
    def session(self):

        return self._master_session

    @property
    def slave_session(self):
        """
        slave session,for execute session.execute(),
        if slave is not give,return master session
        """
        if self._slaves_session:
            return random.choice(self._slaves_session)
        else:
            return self._master_session

    @property
    def Model(self):
        if hasattr(self, '_base'):
            base = self._base
        else:
            base = get_base_model()
            self._base = base
        if self._slaves_session:
            slave = random.choice(self._slaves_session)
            base.query = slave.query_property()
        else:
            base.query = self._master_session.query_property()
        return base

    def _ping_db(self):
        self._master_session.execute('show variables')
        for slave in self._slaves_session:
            slave.execute('show variables')

    def create_db(self):
        self.Model.metadata.create_all(self.engine)

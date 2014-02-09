from sqlalchemy import *
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.mysql import INTEGER


class BaseModel(object):
    created_datetime = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    reversion = Column(INTEGER(10), server_default=text('1'), nullable=False)

    @classmethod
    def get_tablename(cls):
        return cls.__tablename__

    @classmethod
    def set_tablename(cls, value):
        cls.__tablename__ = value

    @property
    def tablename(self):
        return self.__tablename__
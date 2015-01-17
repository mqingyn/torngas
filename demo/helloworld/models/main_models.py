# -*-coding=utf8-*-
# your models module write here
import datetime
from torngas.db.dbalchemy import Model
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref


class BaseModel(Model):
    __abstract__ = True
    __connection_name__ = 'default'

    id = Column(Integer, primary_key=True, nullable=False)


class User(BaseModel):
    """
    user model
    """
    __tablename__ = 'demo_user'

    name = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    created_date = Column(TIMESTAMP, default=datetime.datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    blogs = relationship('Blog', backref=backref('demo_user'))


class Blog(BaseModel):
    """
    blog model
    """
    __tablename__ = 'demo_blog'

    user = Column('user_id', Integer, ForeignKey('demo_user.id'), nullable=False)
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=True)
    created_date = Column(TIMESTAMP, default=datetime.datetime.now, server_default=text('CURRENT_TIMESTAMP'))


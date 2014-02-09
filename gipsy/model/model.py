#-*-coding=utf8-*-
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from torngas.db.dbalchemy import sql_connection
from commonlib.base_model import BaseModel
from sqlalchemy.dialects.mysql import TINYINT

class PictureInfo(sql_connection.connetion,BaseModel):
    _table_name = 'picture_info'




class UserProfile(sql_connection.connetion.gipsy.Model, BaseModel):
    __tablename__ = 'UserProfile'

    portrait_large = Column(String(256), nullable=True)

    portrait_midd = Column(String(256), nullable=True)

    portrait_smaill = Column(String(256), nullable=True)
    # 自我介绍
    summary = Column(String(256), nullable=True)
    # 性别，0：未知，1：男，2：女，3：双性
    gender = Column(TINYINT(1), default=0)

    # 0；未知，1：男，2.女，3：不分性别
    sex_orien = Column(TINYINT(1), default=0)
    # 职位
    position = Column(String(64), nullable=True)
    # 部门
    department = Column(String(64), nullable=True)
    # 公司
    company = Column(Integer(10), default=1)

    userbase_id = Column(Integer(10), ForeignKey('UserBaseInfo.id'), nullable=False)

# user_profile = relationship('UserProfile', backref('UserBaseInfo'), uselist=False)

class UserBaseInfo(sqlconn.get_connetion.aquis.Model, BaseModel):
    __tablename__ = 'UserBaseInfo'

    def __init__(self, username='', usr_psswd=''):
        self.username = username
        self.usr_psswd = usr_psswd


    username = Column(String(16), unique=True, nullable=False)

    usr_psswd = Column(String(45), nullable=False)

    is_alive = Column(Boolean, default=True)

    last_login_time = Column(DateTime, nullable=False, default=datetime.now())

    nickname = Column(String(16), nullable=False, default=u'小可怜')

    email = Column(String(45), unique=True)

    user_profile = relationship('UserProfile', backref=backref('UserBaseInfo'), uselist=False)



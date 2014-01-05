#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
session中间件,支持disk，进程内缓存cache,memcache
"""
import os, time

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import hashlib

    sha1 = hashlib.sha1
except ImportError:
    import sha

    sha1 = sha.new
import hmac, re
from torngas.utils.storage import storage
from torngas.utils.strtools import safestr
from torngas.helpers.logger_helper import logger
from torngas.utils import lazyimport
from middleware_manager import BaseMiddleware
from torngas import Null

settings_module = lazyimport('torngas.helpers.settings_helper')
cache_module = lazyimport('torngas.cache')
rx = re.compile('^[0-9a-fA-F]+$')


class SessionMiddleware(BaseMiddleware):
    def process_init(self, application):
        self._cachestore = cache_module.get_cache(settings_module.settings.SESSION.session_cache_alias)


    def process_request(self, handler):
        session = SessionManager(handler, self._cachestore, settings_module.settings.SESSION)
        session.load_session()
        handler.session = session

    def process_exception(self, ex_object, exception):
        self.session = Null()
        logger.getlogger.error("session middleware error:{0}".format(exception.message))


    def process_response(self, handler):
        if hasattr(handler, "session"):
            handler.session.save()
            del handler.session

    def process_endcall(self, handler):
        pass


"""
sessioin过期策略分为三种情形：
1.固定时间过期，例如10天内没有访问则过期，timeout=xxx
    *cookie策略：每次访问时设置cookie为过期时间
    *缓存策略：每次访问设置缓存失效时间为固定过期时间
2.会话过期，关闭浏览器即过期timeout=0
    *cookie策略：岁浏览器关闭而过期
    *缓存策略：设置缓存失效期为1天，每次访问更新失效期，如果浏览器关闭，则一天后被清除

3.永不过期(记住我)
    *cookie策略：timeout1年
    *缓存策略：1年
"""
_DAY1 = 24 * 60 * 60
_DAY30 = _DAY1 * 30
_VERIFICATION_KEY = '__VERIFID'
__all__ = [
    'Session', 'SessionExpired',
    'Store', 'DiskStore', 'DBStore', 'SimpleCacheStore'
]

session_parameters = storage({
    'session_name': '__TORNADOID',
    'cookie_domain': None,
    'cookie_path': '/',
    'expires': 0, #24 * 60 * 60, # 24 hours in seconds
    'ignore_change_ip': False,
    'httponly': True,
    'secure': False,
    'secret_key': 'fLjUfxqXtfNoIldA0A0J',
    'session_version': 'V1.6'
})


class SessionManager(object):
    _killed = False

    def __init__(self, handler, store, config=session_parameters):

        self._get_cookie = handler.get_cookie
        self._set_cookie = handler.set_cookie
        self.remote_ip = handler.request.remote_ip
        self.store = store

        self.config = storage(config)
        self._data = {}

    def __contains__(self, key):
        return key in self._data

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data.get(key, None)


    def __delitem__(self, key):
        del self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def load_session(self):
        """
        加载session
        :return:
        """
        self.sessionid = self._get_cookie(self.config.session_name)

        if self.sessionid and not self._valid_session_id(self.sessionid):
            self.sessionid = None
            self.expired()

        if self.sessionid:
            if self.sessionid in self.store:
                expires, _data = self.store.get(self.sessionid)
                self._data.update(_data)
                self.config.expires = expires
            self._validate_ip()
            hmac_verif = self._get_cookie(_VERIFICATION_KEY)
            if hmac_verif != self._generate_hmac(self.sessionid):
                self.expired()

        if not self.sessionid:
            self.sessionid = self._create_sessionid()

        self._data['remote_ip'] = self.remote_ip


    def save(self):
        if not self._killed:

            httponly = self.config.httponly
            secure = self.config.secure
            expires = self.config.expires#单位是秒
            cache_expires = expires
            if expires == 0:
                #过期时间为0时，对于tornado来说，是会话有效期，关闭浏览器失效，但是
                #对于cache缓存而言，无法及时捕获会话结束状态，鉴于此，将cache的缓存设置为一天
                #cache在每次请求后会清理过期的缓存
                cache_expires = _DAY1

            if not secure:
                secure = ''

            if not httponly:
                httponly = ''
            set_expire = 0 if expires == 0 else time.time() + expires
            self._set_cookie(
                self.config.session_name,
                self.sessionid,
                domain=self.config.cookie_domain or '',
                expires=set_expire,
                path=self.config.cookie_path,
                secure=secure,
                httponly=httponly)
            self._set_cookie(_VERIFICATION_KEY, self._generate_hmac(self.sessionid),
                             domain=self.config.cookie_domain or '',
                             expires=set_expire,
                             path=self.config.cookie_path,
                             secure=secure,
                             httponly=httponly)
            self.store.set(self.sessionid, ( expires, self._data), cache_expires)

        else:
            self._set_cookie(self.config.session_name, self.sessionid, expires=-1)
            self._set_cookie(_VERIFICATION_KEY, self._generate_hmac(self.sessionid), expires=-1)
            del self.store[self.sessionid]


    def _valid_session_id(self, sessionid):
        """
        验证sessionid格式
        :return:bool
        """

        if sessionid:
            sessionid = sessionid.split('|')[0]

            return rx.match(sessionid)

    def expired(self):
        """
        强制过期
        :return:None
        """
        self._killed = True
        self.save()

    def _create_sessionid(self):
        while True:
            rand = os.urandom(16)
            now = time.time()
            secret_key = self.config.secret_key
            session_id = sha1("%s%s%s%s" % (rand, now, safestr(self.remote_ip), secret_key))
            session_id = session_id.hexdigest()
            if session_id not in self.store:
                break
        return str(session_id).upper() + '|' + self.config.session_version

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.config.secret_key, hashlib.sha1).hexdigest()


    def _validate_ip(self):
        if self.sessionid and self._data.get('remote_ip', None) != self.remote_ip:
            if not self.config.ignore_change_ip:
                return self.expired()

    def set_expire(self, expires):
        self.config.expires = expires
        self.save()


if __name__ == '__main__':
    import doctest

    doctest.testmod()





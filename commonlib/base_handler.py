#-*- coding=utf8 -*-
from torngas.handlers import WebHandler
from container_manager import container
from torngas import Null
from tornado.util import import_object
from torngas.utils.storage import storage
from torngas.helpers.settings_helper import settings
import tornado.web
import commonlib.subject_object as subject_object
from urllib import unquote
import json


class BaseHandler(WebHandler):
    """
    do some your base things
    """
    auth_user_key = '__user_auth'
    login_userid = 0

    code = subject_object.so_code

    @property
    def site_settings(self):

    # expires = self.settings['permanent_session_lifetime'] or None
    # self._session = sessions.Session(self.get_secure_cookie, self.set_secure_cookie, expires_days=expires)
    # return self._session

        if hasattr(self, '_site_settings'):
            return self._site_settings
        else:
            site_sittings_module = import_object('.'.join([self.appname, 'site_settings']))

            if site_sittings_module:
                self._site_settings = site_sittings_module
                return site_sittings_module
            else:
                return Null()

    def render_string(self, template_name, **kwargs):

        kwargs['site_settings'] = self.site_settings
        kwargs['get_flash'] = self.get_flashed_messages
        if not template_name.endswith('.mako'):
            template_name = '.'.join([template_name, 'mako'])
        return super(BaseHandler, self).render_string(template_name, **kwargs)


    def static_url(self, path, include_host=None, **kwargs):
        self.require_setting("static_path", "static_url")
        get_url = self.settings.get("static_handler_class",
                                    tornado.web.StaticFileHandler).make_static_url

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        if include_host:
            base = self.request.protocol + "://" + self.request.host
        else:
            base = ""

        version = self.site_settings.static_version
        return '%s?v=%s' % (base + get_url(self.settings, path, include_version=False, **kwargs), version)


    def set_authorized(self, userid, keep_login=False, **kwargs):
        if userid:
            kwargs['userid'] = userid
            auth_user = storage(kwargs)
            self.login_userid = userid
            self.session[self.auth_user_key] = auth_user
            if keep_login:
                self.session.set_expire(60 * 60 * 24 * 30)

    def get_current_user(self):
        return self.session[self.auth_user_key] \
            if hasattr(self, "session") and self.auth_user_key in self.session else None

    def user_logout(self):
        self.clear_all_cookies()
        del self.session[self.auth_user_key]

    def get_requestbody(self):
        return json.loads(self.request.body)

    def check_xsrf_cookie(self):
        """
        重写xsrf适应angularjs
        """
        try:

            params = json.loads(self.request.body)
        except Exception:
            params = {}
        token = (self.get_argument("_xsrf", None) or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken") or
                 params.get("_xsrf"))
        if not token:
            raise HTTPErrors(403, "'_xsrf' argument missing from POST")
        if self.xsrf_token != token:
            raise tornado.web.HTTPError(403, "XSRF cookie does not match POST argument")



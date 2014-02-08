#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2013,掌阅科技
All rights reserved.

摘    要：
创 建 者：mengqingyun
创建日期：2014-1-24
"""

import json
from torngas.handlers.common_handler import WebHandler
from torngas.cache import get_cache
from tornado import web
from torngas.decorators.async_execute import async_execute
from .. import SITE_SETTINGS
from torngas.inject_factory import factory
from torngas.helpers.logger_helper import logger

class Base(WebHandler):
    def static_url(self, path, include_host=None, **kwargs):
        self.require_setting("static_path", "static_url")
        get_url = self.settings.get("static_handler_class",
                                    web.StaticFileHandler).make_static_url

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        if include_host:
            base = self.request.protocol + "://" + self.request.host
        else:
            base = ""

        version = self.site_settings.static_version
        return '%s?v=%s' % (base + get_url(self.settings, path, include_version=False, **kwargs), version)

    @property
    def site_settings(self):
        return SITE_SETTINGS

    def render(self, template_name, **kwargs):
        kwargs['site_settings'] = self.site_settings
        return super(Base, self).render(template_name, **kwargs)

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
            raise web.HTTPError(403, "'_xsrf' argument missing from POST")
        if self.xsrf_token != token:
            raise web.HTTPError(403, "XSRF cookie does not match POST argument")

    @property
    def cache(self):
        return get_cache("default")


class Index(Base):
    def on_prepare(self):
        pass

    def get(self, group_id=1):


        kw = locals()
        kw.pop('self')

        self.render('gipsy/index.mako', **kw)


if __name__ == '__main__':
    pass
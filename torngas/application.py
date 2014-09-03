#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
from tornado import web
from tornado import version_info
from tornado.log import app_log
from torngas.middleware.manager import Manager
from torngas.settings_manager import settings as config
from tornado import httputil


class Application(web.Application):
    def __init__(self, handlers=None,
                 default_host="",
                 transforms=None,
                 wsgi=False,
                 **settings):

        super(Application, self).__init__(
            handlers=handlers,
            default_host=default_host,
            transforms=transforms,
            wsgi=wsgi, **settings)

        self.middleware_manager = Manager()
        if hasattr(config, 'MIDDLEWARE_CLASSES') and len(config.MIDDLEWARE_CLASSES):
            self.middleware_manager.load(config.MIDDLEWARE_CLASSES)
            self.middleware_manager.run_init(self)

        if version_info[0] > 3:
            this = self

            class HttpRequest(httputil.HTTPServerRequest):
                def __init__(self, *args, **kwargs):
                    super(HttpRequest, self).__init__(*args, **kwargs)
                    this.middleware_manager.set_request(self)
                    this.middleware_manager.run_call(self)

            httputil.HTTPServerRequest = HttpRequest


    def __call__(self, request):
        if version_info[0] < 4:
            try:
                self.middleware_manager.set_request(request)
                self.middleware_manager.run_call(request)
                return web.Application.__call__(self, request)

            except Exception, e:
                app_log.error(e)
                raise

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by mengqingyun on 14-5-22.
from tornado import web
from tornado import version_info
from tornado.log import app_log
from torngas.middleware.manager import MiddlewareManager
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

        self.middleware_manager = MiddlewareManager()
        self.middleware_manager.run_init_hooks(self)

        if version_info[0] > 3:
            this = self

            class HttpRequestHook(httputil.HTTPServerRequest):
                def __init__(self, *args, **kwargs):
                    super(HttpRequestHook, self).__init__(*args, **kwargs)
                    try:
                        this.middleware_manager.run_call_hooks(self)
                    except Exception, ex:
                        app_log.error(ex)

            httputil.HTTPServerRequest = HttpRequestHook


    def __call__(self, request):
        if version_info[0] < 4:
            try:
                self.middleware_manager.run_call_hooks(request)
                return web.Application.__call__(self, request)

            except Exception, e:
                app_log.error(e)
                raise
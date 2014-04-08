#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web as web
from tornado.log import app_log
from torngas.utils import lazyimport


signals_module = lazyimport('torngas.dispatch')
middleware_module = lazyimport('torngas.middleware')


class Application(web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):

        web.Application.__init__(self,
                                 handlers=handlers,
                                 default_host=default_host,
                                 transforms=transforms,
                                 wsgi=wsgi, **settings)

        self.middleware_manager = middleware_module.MiddlewareManager()
        self.middleware_manager.run_init_hooks(self)

    def __call__(self, request):
        try:
            signals_module.signals.call_started.send(sender=self.__class__)
            self.middleware_manager.run_call_hooks(request)
            handler = web.Application.__call__(self, request)
            self.middleware_manager.run_endcall_hooks(handler)
            signals_module.signals.call_finished.send(sender=self.__class__)

        except Exception, e:
            app_log.error(e)
            raise





#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tornado.web as web
from tornado.options import options
from torngas.utils import lazyimport
from torngas.helpers.logger_helper import logger

access_log = logging.getLogger("tornado.access")
signals_module = lazyimport('torngas.dispatch')
middleware_module = lazyimport('torngas.middleware')
logger_module = lazyimport('torngas.helpers.logger_helper')


class AppApplication(web.Application):
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
            logger.getlogger.error(e)
            raise

    def log_request(self, handler):
        status = handler.get_status()
        if status < 400:
            log_method = access_log.info
        elif status < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()

        if request_time > 50.0 or options.debug or status >= 400:
            log_method("%d %s %.2fms", handler.get_status(),
                       handler._request_summary(), request_time)




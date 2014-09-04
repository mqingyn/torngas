#!/usr/bin/env python
# -*- coding: utf-8  -*-

__author__ = 'qingyun.meng'

"""
Created by qingyun.meng on 202014/9/4.
Modify by: qingyun.meng
Description: 
"""
import tornado.locale
from torngas.settings_manager import settings


class HandlerMixin(object):
    _url_kwargs = {}

    def __init__(self, application, request, **kwargs):
        if kwargs:
            self._url_kwargs.update(kwargs)
            kwargs.clear()
        super(HandlerMixin, self).__init__(application, request, **kwargs)

    def prepare(self):
        self.application.middleware_manager.run_request_hooks(self)
        return self.on_prepare()

    def on_prepare(self):
        pass

    def render_string(self, template_name, **kwargs):
        self.application.middleware_manager.run_render_hooks(self, template_name, **kwargs)
        return super(HandlerMixin, self).render_string(template_name, **kwargs)

    def finish(self, chunk=None):
        # finish之前可能执行过多次write，反而chunk可能为None
        # 真正的chunk数据在self._write_buffer中，包含历次write的数据
        # 这里将chunk数据write进_write_buffer中，然后将chunk置空
        if chunk:
            self.write(chunk)
            chunk = None
        self.application.middleware_manager.run_response_hooks(self, self._write_buffer)
        super(HandlerMixin, self).finish(chunk)

    def write(self, chunk, status=None):
        if status:
            self.set_status(status)
        super(HandlerMixin, self).write(chunk)


    def on_finish(self):
        self.application.middleware_manager.run_endcall_hooks(self)
        self.complete_finish()

    def complete_finish(self):
        pass

    def get_user_locale(self):
        if settings.TRANSLATIONS_CONF.use_accept_language:
            return None

        return tornado.locale.get(settings.TRANSLATIONS_CONF.locale_default)


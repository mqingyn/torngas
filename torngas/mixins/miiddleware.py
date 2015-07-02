#!/usr/bin/env python
# -*- coding: utf-8  -*-


class MiddlewareHandlerMixin(object):
    _url_kwargs = {}

    def __init__(self, application, request, **kwargs):
        if kwargs:
            self._url_kwargs.update(kwargs)
            kwargs.clear()
        super(MiddlewareHandlerMixin, self).__init__(application, request, **kwargs)

    def prepare(self):
        res = self.application.middleware_fac.run_request(self)
        self.on_prepare()
        return res

    def on_prepare(self):
        pass

    def render_string(self, template_name, **kwargs):
        self.application.middleware_fac.run_render(self, template_name, **kwargs)
        return super(MiddlewareHandlerMixin, self).render_string(template_name, **kwargs)

    def finish(self, chunk=None):
        # finish之前可能执行过多次write，反而chunk可能为None
        # 真正的chunk数据在self._write_buffer中，包含历次write的数据
        # 这里将chunk数据write进_write_buffer中，然后将chunk置空
        if chunk:
            self.write(chunk)
            chunk = None
        self.application.middleware_fac.run_response(self, self._write_buffer)
        super(MiddlewareHandlerMixin, self).finish(chunk)

    def write(self, chunk, status=None):
        if status:
            self.set_status(status)
        super(MiddlewareHandlerMixin, self).write(chunk)

    def log_exception(self, typ, value, tb):
        """重写404请求的异常处理
        """
        if not self.application.middleware_fac.run_exception(self, typ, value, tb):
            super(MiddlewareHandlerMixin, self).log_exception(typ, value, tb)

    def on_finish(self):
        super(MiddlewareHandlerMixin, self).on_finish()
        self.application.middleware_fac.run_endcall(self)
        self.complete_finish()

    def complete_finish(self):
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import sys
import tornado
import httplib
import os
from tornado.web import RequestHandler
from tornado import template


class UncaughtExceptionMixin(object):
    def get_error_html(self, status_code, **kwargs):

        def get_snippet(fp, target_line, num_lines):
            if fp.endswith('.html'):
                fp = os.path.join(self.get_template_path(), fp)

            half_lines = (num_lines / 2)
            try:
                with open(fp) as f:
                    all_lines = [line for line in f]

                    return ''.join(all_lines[target_line - half_lines:target_line + half_lines])
            except Exception, ex:
                return ''

        if not self.application.settings.get('debug', False):
            if hasattr(self, 'exception_response'):
                # 如果handler存在此属性，将返回属性内容
                return self.exception_response
            full_message = kwargs.get('exception', None)
            if not full_message or unicode(full_message) == '':
                full_message = 'Server error.'

            return "<html><title>%(code)d: %(message)s</title><body>\
            <h1>%(code)d: %(message)s</h1>%(full_message)s</body></html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
                "full_message": full_message,
            }

        else:
            exception = kwargs.get('exception', None)
            resource = os.path.split(os.path.dirname(__file__))[0]
            tmpl_file = '/resource/exception.html'

            def render_string(template_name, **kw):
                template_path = self.get_template_path()
                if not template_path:
                    frame = sys._getframe(0)
                    web_file = frame.f_code.co_filename
                    while frame.f_code.co_filename == web_file:
                        frame = frame.f_back
                    template_path = os.path.dirname(frame.f_code.co_filename)
                with RequestHandler._template_loader_lock:
                    settings = self.application.settings
                    kwarg = {}

                    if "autoescape" in settings:
                        kwarg["autoescape"] = settings["autoescape"]
                    loader = template.Loader(template_path, **kwarg)
                t = loader.load(template_name)
                namespace = self.get_template_namespace()
                namespace.update(kw)
                return t.generate(**namespace)

            return render_string("%s%s" % (resource, tmpl_file),
                                 get_snippet=get_snippet,
                                 exception=exception,
                                 traceback=traceback,
                                 sys=sys, tornado=tornado,
                                 status_code=status_code, os=os,
                                 kwargs=kwargs)

    def write_error(self, status_code, **kwargs):

        if 'exc_info' in kwargs:
            exc_info = kwargs.pop('exc_info')
            kwargs['exception'] = exc_info[1]

        return self.finish(self.get_error_html(status_code, **kwargs))

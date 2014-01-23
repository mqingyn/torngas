#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import os
from tornado.escape import json_encode, json_decode
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
                self.logger.error(ex)

                return ''

        if self.application.settings.get('debug', False) is False:
            full_message = kwargs.get('exception', None)
            if not full_message or unicode(full_message) == '':
                full_message = 'Sky is falling!'

            return "<html><title>%(code)d: %(message)s</title><body><h1>%(code)d: %(message)s</h1>%(full_message)s</body></html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
                "full_message": full_message,
            }

        else:
            exception = kwargs.get('exception', None)
            resource = os.path.split(os.path.dirname(__file__))[0]
            tmpl_file = '/resource/exception.html'
            import traceback
            import sys
            import tornado

            return self.render_string(resource + tmpl_file, get_snippet=get_snippet,
                                      exception=exception, traceback=traceback, sys=sys, tornado=tornado,
                                      status_code=status_code, os=os, kwargs=kwargs)

    def write_error(self, status_code, **kwargs):

        if 'exc_info' in kwargs:
            exc_info = kwargs.pop('exc_info')
            kwargs['exception'] = exc_info[1]

        return self.finish(self.get_error_html(status_code, **kwargs))


class FlashMessageMixIn(object):
    """
        Store a message between requests which the user needs to see.

        views
        -------

        self.flash("Welcome back, %s" % username, 'success')

        base.html
        ------------

        {% set messages = handler.get_flashed_messages() %}
        {% if messages %}
        <div id="flashed">
            {% for category, msg in messages %}
            <span class="flash-{{ category }}">{{ msg }}</span>
            {% end %}
        </div>
        {% end %}
    """
    _flash_name = "__flhMsg"

    def flash(self, message, category='message'):
        messages = self.messages()
        messages.append((category, message))
        self.set_secure_cookie(self._flash_name, json_encode(messages))

    def messages(self):
        messages = self.get_secure_cookie(self._flash_name)
        messages = json_decode(messages) if messages else []
        return messages

    def get_flashed_messages(self):
        messages = self.messages()
        self.clear_cookie(self._flash_name)
        return messages



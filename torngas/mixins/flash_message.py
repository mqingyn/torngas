#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.escape import json_encode, json_decode


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

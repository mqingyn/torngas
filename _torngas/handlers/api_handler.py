#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from torngas.exception import APIError
from common_handler import CommonHandler


class ApiHandler(CommonHandler):
    def get_format(self):
        format = self.get_argument('format', None)
        if not format:
            accept = self.request.headers.get('Accept')
            if accept:
                if 'javascript' in accept:
                    format = 'jsonp'
                else:
                    format = 'json'
        return format or 'json'

    def write_api(self, obj, nofail=False):
        format = self.get_format()
        if format == 'json':
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(obj))
        elif format == 'jsonp':
            self.set_header("Content-Type", "application/javascript")
            callback = self.get_argument('callback', 'callback')
            self.write('%s(%s);' % (callback, json.dumps(obj)))
        elif nofail:
            self.write(json.dumps(obj))
        else:
            raise APIError(400, 'Unknown response format requested: %s' % format)


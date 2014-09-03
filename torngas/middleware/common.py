#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common middleware
"""
from torngas.middleware import BaseMiddleware
from torngas.settings_manager import settings
from torngas.exception import Http404, HttpForbiddenError
from tornado.log import gen_log
from tornado.web import HTTPError


def validate_illegal(query, illegals):
    if any([query.find(s) >= 0 for s in illegals]):
        raise HttpForbiddenError("Contains illegal arguments.")


class CommonMiddleware(BaseMiddleware):
    def process_call(self, request, next, finish):
        if settings.REMOVE_SLASH_ALL and request.path.endswith("/"):
            uri = request.path.rstrip("/")
            if uri:  # don't try to redirect '/' to ''
                request.path = uri
        next()

    def process_request(self, handler, next, finish):
        current_user_agent = handler.request.headers.get('User-Agent', None)
        if current_user_agent:
            for user_agent in settings.DISALLOWED_USER_AGENTS:
                if user_agent.search(current_user_agent):
                    self.is_finished = True
                    gen_log.error('Forbidden (User agent): %s', handler.request.path, extra={
                        'status_code': 403,
                        'request': handler.request
                    })
                    raise HttpForbiddenError()

        if settings.ILLEGAL_CHARACTER_FORBIDDEN:
            # 验证是否包含非法字符
            illegals = settings.ILLEGAL_CHARACTER
            if handler.request.arguments:
                query = str(handler.request.query_arguments)
                validate_illegal(query, illegals)
            if handler.request.body:
                query = str(handler.request.body)
                validate_illegal(query, illegals)
        next()

    def process_exception(self, ex_obj, exec_info, next, finish):
        if HTTPError in exec_info[0].__bases__:
            raise

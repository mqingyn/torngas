#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Torngas Whitelist Module

"""
from tornado import web
import types
from torngas.settings_manager import settings


def whitelisted(argument=None):
    """
    白名单，如果在参数中列出可访问的ip或在配置文件中列出，则被标记的请求方法仅可允许白名单ip访问
    :param argument: whitelist ip list
    :return:bool
    """

    def is_whitelisted(remote_ip, whitelist):
        if remote_ip in whitelist:
            return True
        else:
            return False

    if type(argument) is types.FunctionType:

        def wrapper(self, *args, **kwargs):
            white_setting = settings.WHITELIST
            if white_setting:
                if is_whitelisted(self.request.remote_ip,
                                  settings.WHITELIST):
                    return argument(self, *args, **kwargs)
                raise web.HTTPError(403)
            else:
                raise web.HTTPError(403)

        return wrapper

    else:
        if isinstance(argument, str):
            argument = [argument]

        elif not isinstance(argument, list):
            raise ValueError('whitelisted requires no parameters or '
                             'a string or list')

        def argument_wrapper(method):

            def validate(self, *args, **kwargs):
                if is_whitelisted(self.request.remote_ip, argument):
                    return method(self, *args, **kwargs)
                raise web.HTTPError(403)

            return validate

        return argument_wrapper

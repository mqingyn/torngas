#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from tornado.template import Loader
from torngas.helpers.settings_helper import settings

_CACHE = FileSystemBytecodeCache()
_LOADER = FileSystemLoader([])
_JINJA_ENV = Environment(bytecode_cache=_CACHE,
                         autoescape=settings.TEMPLATE_CONFIG.autoescape,
                         cache_size=settings.TEMPLATE_CONFIG.cache_size,
                         auto_reload=settings.TEMPLATE_CONFIG.filesystem_checks,
                         loader=_LOADER)


class Jinja2TemplateLoader(Loader):
    def __init__(self, root_directory='', **kwargs):
        super(Jinja2TemplateLoader, self).__init__(root_directory, **kwargs)
        path = os.path.abspath(root_directory)
        _JINJA_ENV.loader.searchpath = [path]

        cache_dir = os.path.abspath(settings.TEMPLATE_CONFIG.cache_directory)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        _CACHE.directory = cache_dir


    def load(self, name, parent_path=None):
        with self.lock:
            if os.path.isabs(name):
                path, file = os.path.split(name)
                _JINJA_ENV.loader.searchpath = [path]
                template = _JINJA_ENV.get_template(file)
            else:
                template = _JINJA_ENV.get_template(name)
            template.generate = template.render
            return template


    def reset(self):
        if hasattr(_JINJA_ENV, 'bytecode_cache') and _JINJA_ENV.bytecode_cache:
            _JINJA_ENV.bytecode_cache.clear()
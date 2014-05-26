#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from tornado.template import Loader
from torngas.settings_manager import settings
from jinja2.defaults import *
from jinja2.runtime import Undefined

_CACHE = FileSystemBytecodeCache()
_LOADER = FileSystemLoader([])
cfg = settings.TEMPLATE_CONFIG
_JINJA_ENV = Environment(bytecode_cache=_CACHE,
                         autoescape=cfg.get('autoescape', False),
                         cache_size=cfg.get('cache_size', 50),
                         auto_reload=cfg.get('filesystem_checks', True),
                         loader=_LOADER,
                         block_start_string=cfg.get('block_start_string', BLOCK_START_STRING),
                         block_end_string=cfg.get('block_end_string', BLOCK_END_STRING),
                         variable_start_string=cfg.get('variable_start_string', VARIABLE_START_STRING),
                         variable_end_string=cfg.get('variable_end_string', VARIABLE_END_STRING),
                         comment_start_string=cfg.get('comment_start_string', COMMENT_START_STRING),
                         comment_end_string=cfg.get('comment_end_string', COMMENT_END_STRING),
                         line_statement_prefix=cfg.get('line_statement_prefix', LINE_STATEMENT_PREFIX),
                         line_comment_prefix=cfg.get('line_comment_prefix', LINE_COMMENT_PREFIX),
                         trim_blocks=cfg.get('trim_blocks', TRIM_BLOCKS),
                         lstrip_blocks=cfg.get('lstrip_blocks', LSTRIP_BLOCKS),
                         newline_sequence=cfg.get('newline_sequence', NEWLINE_SEQUENCE),
                         keep_trailing_newline=cfg.get('keep_trailing_newline', KEEP_TRAILING_NEWLINE),
                         extensions=cfg.get('extensions', ()),
                         optimized=cfg.get('optimized', True),
                         undefined=cfg.get('undefined', Undefined),
                         finalize=cfg.get('finalize', None))


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
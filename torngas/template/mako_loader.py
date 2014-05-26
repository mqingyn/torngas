#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from mako.lookup import TemplateLookup
from tornado.template import Loader
from torngas.settings_manager import settings

cfg = settings.TEMPLATE_CONFIG
_lookup = TemplateLookup(input_encoding=cfg.get('input_encoding', 'utf-8'),
                         output_encoding=cfg.get('output_encoding', 'utf-8'),
                         encoding_errors=cfg.get('encoding_errors', 'replace'),
                         filesystem_checks=cfg.get('filesystem_checks', True),
                         default_filters=cfg.get('default_filters', ['decode.utf8']),
                         collection_size=cfg.get('collection_size', -1),
                         format_exceptions=cfg.get('format_exceptions', False),
                         directories=cfg.get('directories', None),
                         module_directory=cfg.get('module_directory', None),
                         error_handler=cfg.get('error_handler', None),
                         disable_unicode=cfg.get('disable_unicode', False),
                         bytestring_passthrough=cfg.get('bytestring_passthrough', False),
                         cache_args=cfg.get('cache_args', False),
                         cache_impl=cfg.get('cache_impl', 'beaker'),
                         cache_enabled=cfg.get('cache_enabled', True),
                         cache_type=cfg.get('cache_type', None),
                         cache_dir=cfg.get('cache_dir', None),
                         cache_url=cfg.get('cache_url', None),
                         modulename_callable=cfg.get('modulename_callable', None),
                         module_writer=cfg.get('module_writer', None),
                         buffer_filters=cfg.get('buffer_filters', ()),
                         strict_undefined=cfg.get('strict_undefined', False),
                         imports=cfg.get('imports', None),
                         future_imports=cfg.get('future_imports', None),
                         enable_loop=cfg.get('enable_loop', True),
                         preprocessor=cfg.get('preprocessor', None),
                         lexer_cls=cfg.get('lexer_cls', None))


class MakoTemplateLoader(Loader):
    def __init__(self, root_directory, **kwargs):
        super(MakoTemplateLoader, self).__init__(root_directory, **kwargs)
        self.path = os.path.abspath(root_directory)
        self.module_directory = os.path.abspath(settings.TEMPLATE_CONFIG.cache_directory)

    def load(self, name, parent_path=None):
        with self.lock:
            _lookup.module_directory = self.module_directory
            _lookup.template_args['module_directory'] = self.module_directory
            if os.path.isabs(name):
                path, file = os.path.split(name)
                _lookup.directories = [path]

                template = _lookup.get_template(file)
            else:
                _lookup.directories = [self.path]

                template = _lookup.get_template(name)
        template.generate = template.render

        return template

    def reset(self):
        pass
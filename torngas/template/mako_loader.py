#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from mako.lookup import TemplateLookup
from tornado.template import Loader
from torngas.helpers.settings_helper import settings

_lookup = TemplateLookup(input_encoding='utf-8',
                         output_encoding='utf-8',
                         encoding_errors='replace',
                         filesystem_checks=settings.TEMPLATE_CONFIG.filesystem_checks,

                         default_filters=['decode.utf8'],
                         collection_size=settings.TEMPLATE_CONFIG.collection_size,
                         format_exceptions=settings.TEMPLATE_CONFIG.format_exceptions)


class MakoTemplateLoader(Loader):
    def __init__(self, root_directory, **kwargs):
        super(MakoTemplateLoader, self).__init__(root_directory, **kwargs)
        self.path = os.path.abspath(root_directory)
        self.module_directory = os.path.abspath(settings.TEMPLATE_CONFIG.cache_directory)

    def load(self, name,parent_path=None):
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
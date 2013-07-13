import os

from mako.lookup import TemplateLookup
from tornado.template import Loader
from torngas.helpers.settings_helper import settings


class MakoTemplateLoader(Loader):
    def __init__(self, root_directory, app_name, **kwargs):
        super(MakoTemplateLoader, self).__init__(root_directory, **kwargs)
        path = os.path.abspath(root_directory)
        self._lookup = TemplateLookup(directories=path, input_encoding='utf-8',
                                      output_encoding='utf-8',
                                      encoding_errors='replace',
                                      filesystem_checks=settings.TEMPLATE_CONFIG.filesystem_checks,
                                      module_directory=os.path.abspath(
                                          os.path.join(settings.TEMPLATE_CONFIG.cache_directory, app_name)),
                                      default_filters=['decode.utf8'],
                                      collection_size=settings.TEMPLATE_CONFIG.collection_size,
                                      format_exceptions=settings.TEMPLATE_CONFIG.format_exceptions)

    def load(self, name):
        with self.lock:
            if os.path.isabs(name):
                path, file = os.path.split(name)
                self._lookup.directories = [path]
                template = self._lookup.get_template(file)
            else:
                template = self._lookup.get_template(name)
            template.generate = template.render

            return template

    def reset(self):
        pass
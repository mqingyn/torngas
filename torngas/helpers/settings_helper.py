#-*-coding=utf8-*-
import os
from tornado.util import import_object
from tornado.options import options
from torngas.exception import ConfigError
from torngas.utils.storage import storage
from torngas import global_settings
import warnings


class Settings(object):
    def __init__(self):
        pass

    def get_settings(self, name):
        if not hasattr(self, '._setting'):
            try:
                settings_env = os.environ.get("TORNGAS_PROJECT_NAME", '')
                # self.settings_module = global_setttings
                self.settings_module = import_object('.'.join([settings_env, options.setting]))
            except ImportError:
                self.settings_module = global_settings
                warnings.warn('settings file import error. using global settings now.')
            self._config = self.settings_module

        if hasattr(self._config, name):
            return getattr(self._config, name)
        elif hasattr(self._config, name):
            return getattr(self._config, name)
        else:
            raise ConfigError('settings "%s" not exist!' % name)

    def __getattr__(self, item):
        setting = self.get_settings(item)
        return storage(setting) if type(setting) is dict else setting


settings = Settings()

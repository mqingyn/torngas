#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from tornado.util import import_object
from tornado.options import options
from torngas.exception import ConfigError
from torngas.utils.storage import storage
from torngas import global_settings
import warnings

SETTINGS_MODULE = "SETTINGS_MODULE"


class Settings(object):
    def __contains__(self, item):
        setting = self.settings_module
        return hasattr(setting, item)

    def __getattr__(self, item):
        setting = self.settings_module

        if hasattr(setting, item):
            if item in ('TORNADO_CONF', 'LOG_CONFIG', 'SESSION', 'TEMPLATE_CONFIG',):
                config = getattr(global_settings, item)
                user_config = getattr(setting, item)
                config.update(user_config)
            else:
                config = getattr(setting, item)

        elif hasattr(global_settings, item):
            config = getattr(global_settings, item)
        else:
            raise ConfigError('settings "%s" not exist!' % item)

        return storage(config) if type(config) is dict else config

    @property
    def settings_module(self):
        if not hasattr(self, '__conf'):
            try:
                if os.environ.get(SETTINGS_MODULE, None):
                    self.__conf = import_object(os.environ[SETTINGS_MODULE])
                else:
                    self.__conf = import_object('.'.join(['settings', options.settings]))
            except AttributeError:
                self.__conf = import_object('.'.join(["settings", "setting"]))
            except ImportError:
                warnings.warn(
                    'settings file import error. using global settings now. you need create "setting" files')
                self.__conf = global_settings
        return self.__conf


settings = Settings()


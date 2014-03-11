#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

    def __getattr__(self, item):

        def get_settings(name):
            if not hasattr(self, '._setting'):
                try:
                    if os.environ.get("SETTINGS_MODULE",None):
                        settings_module =import_object(os.environ["SETTINGS_MODULE"])
                    else:
                        settings_module = import_object('.'.join(["settings", options.setting]))
                except AttributeError:
                    settings_module = import_object('.'.join(["settings", "setting"]))
                except ImportError:
                    settings_module = global_settings
                    warnings.warn(
                        'settings file import error. using global settings now. you need create "settings" module')

                self._config = settings_module

            if hasattr(self._config, name):
                return getattr(self._config, name)
            elif hasattr(self._config, name):
                return getattr(self._config, name)
            else:
                raise ConfigError('settings "%s" not exist!' % name)

        setting = get_settings(item)
        return storage(setting) if type(setting) is dict else setting


settings = Settings()

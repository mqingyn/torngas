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

    def __contains__(self, item):
        setting = self._get_settings()
        return hasattr(setting, item)

    def __getattr__(self, item):
        setting = self._get_settings()

        if hasattr(setting, item):
            config = getattr(setting, item)
        elif hasattr(global_settings, item):
            config = getattr(global_settings, item)
        else:
            raise ConfigError('settings "%s" not exist!' % item)

        return storage(config) if type(config) is dict else config

    def _get_settings(self):
        if not hasattr(self, 'setting'):
            try:
                if os.environ.get("SETTINGS_MODULE", None):
                    settings_module = import_object(os.environ["SETTINGS_MODULE"])
                else:
                    settings_module = import_object('.'.join(["settings", options.setting]))
            except AttributeError:
                settings_module = import_object('.'.join(["settings", "setting"]))
            except ImportError:
                settings_module = global_settings
                warnings.warn(
                    'settings file import error. using global settings now. you need create "settings" module')

            self._config = settings_module

        return self._config


settings = Settings()

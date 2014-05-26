#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from tornado.util import import_object
from tornado.options import options
from torngas.exception import ConfigError
from torngas.utils.storage import storage
from torngas import global_settings
import warnings

SETTINGS_MODULE_ENVIRON = "SETTINGS_MODULE"


class Settings(object):
    def __contains__(self, item):
        setting = Settings.settings_object()
        return hasattr(setting, item)

    def __getattr__(self, item):
        setting = Settings.settings_object()

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

    @classmethod
    def settings_object(cls):
        if not hasattr(cls, '_sett'):
            try:
                sett_obj = import_object(options.settings)
                cls._sett = sett_obj
            except AttributeError:
                if os.environ.get(SETTINGS_MODULE_ENVIRON, None):
                    cls._sett = import_object(os.environ[SETTINGS_MODULE_ENVIRON])
                else:
                    raise ConfigError(
                        'tornado.options not have "settings",You may try to use settings \
                         before "define settings module"')
            except ImportError:
                warnings.warn(
                    'settings file import error. using global settings now. you need create "setting" files')
                cls._sett = global_settings
        return cls._sett


settings = Settings()


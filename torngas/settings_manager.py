#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import warnings

from tornado.util import import_object
from tornado.options import options

from exception import ConfigError
from torngas.storage import storage
from torngas import global_settings

SETTINGS_MODULE_ENVIRON = "TORNGAS_APP_SETTINGS"


class _Settings(object):
    def __contains__(self, item):
        setting = _Settings.settings_object()
        return hasattr(setting, item)

    def __getattr__(self, item):
        setting = _Settings.settings_object()
        if hasattr(setting, item):
            config = getattr(setting, item)
        else:
            raise ConfigError('settings "%s" not exist!' % item)

        return storage(config) if type(config) is dict else config

    @classmethod
    def settings_object(cls):

        if not hasattr(cls, '_sett'):
            cls._sett = global_settings
            try:
                sett_obj = import_object(options.settings)
                cls._sett.__dict__.update(sett_obj.__dict__)
            except AttributeError:
                if os.environ.get(SETTINGS_MODULE_ENVIRON, None):
                    sett_obj = import_object(os.environ[SETTINGS_MODULE_ENVIRON])
                    cls._sett.__dict__.update(sett_obj.__dict__)
                else:
                    raise ConfigError(
                        'tornado.options not have "settings",You may try to use settings before "define settings module"')
            except ImportError:
                cls._sett = global_settings
                warnings.warn(
                    'settings file import error.')

        return cls._sett


settings = _Settings()

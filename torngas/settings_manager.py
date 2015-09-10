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
            except Exception:
                if os.environ.get(SETTINGS_MODULE_ENVIRON, None):
                    try:
                        sett_obj = import_object(os.environ[SETTINGS_MODULE_ENVIRON] or None)
                        cls._sett.__dict__.update(sett_obj.__dict__)
                    except:
                        warnings.warn('settings import error.')

        return cls._sett


settings = _Settings()

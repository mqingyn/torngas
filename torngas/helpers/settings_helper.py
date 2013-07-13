#-*-coding=utf8-*-
import os
from tornado.util import import_object
from tornado.options import options
from torngas.exception import ConfigError
from torngas.utils.storage import storage
import warnings


class Settings(object):
    def __init__(self):
        pass

    def get_settings(self, name):
        """

        :param name: 配置名
        :return:配置项
        """
        if not hasattr(self, '._config'):
            global_setttings = import_object('torngas.global_settings')
            if self._get_settings_env():
                try:
                    settings_module = import_object(self._get_settings_env())
                except ImportError:
                    settings_module = global_setttings
                    warnings.warn('config import error. but now,using global settings.')
            else:
                settings_module = global_setttings
            self._config = settings_module

        if hasattr(self._config, name):
            return getattr(self._config, name)
        elif hasattr(self._config, name):
            return getattr(self._config, name)
        else:
            raise ConfigError('config "%s" not exist!' % name)


    def _get_settings_env(self):
        try:
            if options.config == 'devel':
                settings_env = os.environ["TORNGAS_DEV_SETTINGS_MODULE"]
            elif options.config == 'functest':
                settings_env = os.environ["TORNGAS_TEST_SETTINGS_MODULE"]
            elif options.config == 'production':
                settings_env = os.environ["TORNGAS_ONLINE_SETTINGS_MODULE"]
            else:
                settings_env = os.environ["TORNGAS_DEV_SETTINGS_MODULE"]
            return settings_env
        except KeyError:
            warnings.warn('need a app level settings file. but now,using global settings.')


    def __getattr__(self, item):
        setting = self.get_settings(item)
        return storage(setting) if type(setting) is dict else setting


settings = Settings()

if __name__ == "__main__":
    os.environ.setdefault("TORNGAS_ONLINE_SETTINGS_MODULE", "aquis_app.settings")

    print settings.APPS_TEMPLATES_DIR
    print settings.CACHES['default']
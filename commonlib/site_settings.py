import yaml
from torngas.exception import ConfigError
from torngas.utils import lazyimport
import os

__all__ = ['SiteSettings']
settings_module = lazyimport('torngas.helpers.settings_helper')
cache_module = lazyimport('torngas.cache')
_YAML_CACHE_KEY = '$yaml_sitesettings_cache_'


class SiteSettings(object):
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path

    def get(self):
        if settings_module.settings.TORNADO_CONF.debug:
            cache = cache_module.get_cache("dummy")
        else:
            cache = cache_module.cache
        yaml_cfg = cache.get(_YAML_CACHE_KEY)
        if not yaml_cfg:

            setting_file = os.path.join(self.cfg_path, settings_module.settings.SITE_SETTINGS_FILE)
            if not os.path.exists(setting_file):
                raise ConfigError('appsettings file not found. :%s' % setting_file)
            else:
                with open(setting_file, 'r') as filestream:
                    yaml_cfg = yaml.load(filestream)
                    cache_module.cache.set(_YAML_CACHE_KEY, yaml_cfg, timeout=120)

        return yaml_cfg


    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        yaml_cfg = self.get()
        return yaml_cfg[item] if item in yaml_cfg else None



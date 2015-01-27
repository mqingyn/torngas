"""
Caching framework.
"""
from threading import local
from torngas.settings_manager import settings

from torngas.cache.backends.base import (
    InvalidCacheBackendError, CacheKeyWarning, BaseCache)

from tornado.util import import_object
from torngas.exception import ConfigError
from tornado.ioloop import PeriodicCallback


BACKENDS = {
    'memcached': 'memcached',
    'localcache': 'localcache',
    'dummy': 'dummy',
    'redis': 'rediscache'
}

DEFAULT_CACHE_ALIAS = 'default'
DEFAULT_REDIS_ALIAS = 'default_redis'
DEFAULT_MEMCACHED_ALIAS = 'default_memcache'
DEFAULT_DUMMY_ALIAS = 'dummy'

if DEFAULT_CACHE_ALIAS not in settings.CACHES:
    raise ConfigError("You must define a '%s' cache" % DEFAULT_CACHE_ALIAS)


def _create_cache(backend, **kwargs):
    try:
        # Try to get the CACHES entry for the given backend name first
        try:
            conf = settings.CACHES[backend]
        except KeyError:
            try:
                # Trying to import the given backend, in case it's a dotted path
                import_object(backend)
            except ImportError as e:
                raise InvalidCacheBackendError("Could not find backend '%s': %s" % (
                    backend, e))
            location = kwargs.pop('LOCATION', '')
            params = kwargs
        else:
            params = conf.copy()
            params.update(kwargs)
            backend = params.pop('BACKEND')
            location = params.pop('LOCATION', '')
        backend_cls = import_object(backend)
    except ImportError as e:
        raise InvalidCacheBackendError(
            "Could not find backend '%s': %s" % (backend, e))
    return backend_cls(location, params)


class CacheHandler(object):
    """
    A Cache Handler to manage access to Cache instances.

    Ensures only one instance of each alias exists per thread.
    """

    def __init__(self):
        self._caches = local()

    def __getitem__(self, alias):
        try:
            return self._caches.caches[alias]
        except AttributeError:
            self._caches.caches = {}
        except KeyError:
            pass

        if alias not in settings.CACHES:
            raise InvalidCacheBackendError(
                "Could not find config for '%s' in settings.CACHES" % alias
            )

        cache = _create_cache(alias)
        if hasattr(cache, 'clear_expires'):
            PeriodicCallback(cache.clear_expires, 1000 * 1800).start()
        self._caches.caches[alias] = cache
        return cache


    def all(self):
        return getattr(self._caches, 'caches', {}).values()


caches = CacheHandler()


class DefaultCacheProxy(object):
    """
    Proxy access to the default Cache object's attributes.

    This allows the legacy `cache` object to be thread-safe using the new
    ``caches`` API.
    """

    def __getattr__(self, name):
        return getattr(caches[DEFAULT_CACHE_ALIAS], name)

    def __setattr__(self, name, value):
        return setattr(caches[DEFAULT_CACHE_ALIAS], name, value)

    def __delattr__(self, name):
        return delattr(caches[DEFAULT_CACHE_ALIAS], name)

    def __contains__(self, key):
        return key in caches[DEFAULT_CACHE_ALIAS]

    def __eq__(self, other):
        return caches[DEFAULT_CACHE_ALIAS] == other

    def __ne__(self, other):
        return caches[DEFAULT_CACHE_ALIAS] != other


cache = DefaultCacheProxy()


def close_caches(**kwargs):
    # Some caches -- python-memcached in particular -- need to do a cleanup at the
    # end of a request cycle. If not implemented in a particular backend
    # cache.close is a no-op
    for cache in caches.all():
        cache.close()

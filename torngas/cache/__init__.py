"""
torngas cache--from django "Caching framework."

This package defines set of cache backends that all conform to a simple API.
In a nutshell, a cache is a set of values -- which can be any object that
may be pickled -- identified by string keys.  For the complete API, see
the abstract BaseCache class in torngas.cache.backends.base.

Client code should not access a cache backend directly; instead it should
either use the "cache" variable made available here, or it should use the
get_cache() function made available here. get_cache() takes a backend URI
(e.g. "memcached://127.0.0.1:11211/") and returns an instance of a backend
cache class.

See docs/topics/cache.txt for information on the public API.
"""
try:
    from urllib.parse import parse_qsl
except ImportError:     # Python 2
    from urlparse import parse_qsl

from torngas.exception import ConfigError
from torngas.helpers import settings_helper
from backends.base import (
    InvalidCacheBackendError, CacheKeyWarning, BaseCache)
from tornado.util import import_object
from tornado.ioloop import PeriodicCallback
from torngas.dispatch import signals

__all__ = [
    'get_cache', 'cache', 'DEFAULT_CACHE_ALIAS'
]

# Name for use in settings file --> name of module in "backends" directory.
# Any backend scheme that is not in this dictionary is treated as a Python
# import path to a custom backend.
BACKENDS = {
    'memcached': 'memcached',
    'localcache': 'localcache',
    'file': 'filebased',
    'dummy': 'dummy',
}

DEFAULT_CACHE_ALIAS = 'default'
DEFAULT_REDIS_ALIAS = 'default_redis'
FEFAULT_MEMCACHED_ALIAS = 'default_memcache'
if DEFAULT_CACHE_ALIAS not in settings_helper.settings.CACHES:
    raise ConfigError("You must define a '%s' cache" % DEFAULT_CACHE_ALIAS)


def parse_backend_conf(backend, **kwargs):
    """
    Helper function to parse the backend configuration
    that doesn't use the URI notation.
    """
    # Try to get the CACHES entry for the given backend name first
    conf = settings_helper.settings.CACHES.get(backend, None)
    if conf is not None:
        args = conf.copy()
        args.update(kwargs)
        backend = args.pop('BACKEND')
        location = args.pop('LOCATION', '')
        return backend, location, args
    else:
        try:
            # Trying to import the given backend, in case it's a dotted path
            mod_path, cls_name = backend.rsplit('.', 1)
            mod = import_object(mod_path)
            backend_cls = getattr(mod, cls_name)
        except (AttributeError, ImportError, ValueError):
            raise InvalidCacheBackendError("Could not find backend '%s'" % backend)
        location = kwargs.pop('LOCATION', '')
        return backend, location, kwargs


def get_cache(backend, **kwargs):
    """
    Function to load a cache backend dynamically. This is flexible by design
    to allow different use cases:

    To load a backend with the old URI-based notation::

        cache = get_cache('locmem://')

    To load a backend that is pre-defined in the settings::

        cache = get_cache('default')

    To load a backend with its dotted import path,
    including arbitrary options::

        cache = get_cache('torngas.cache.backends.memcached.MemcachedCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 30,
        })

    """
    try:
        backend, location, params = parse_backend_conf(backend, **kwargs)
        mod_path, cls_name = backend.rsplit('.', 1)
        mod = import_object(mod_path)
        backend_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError) as e:
        raise InvalidCacheBackendError(
            "Could not find backend '%s': %s" % (backend, e))
    cache = backend_cls(location, params)
    # Some caches -- python-memcached in particular -- need to do a cleanup at the
    # end of a request cycle. If the cache provides a close() method, wire it up
    # here.
    if hasattr(cache, 'close'):
        signals.call_finished.connect(cache.close)
    if hasattr(cache, 'clear_expires'):
        # signals.call_finished.connect(cache.clear_expires)
        #every half an hour,clear expires cache items
        PeriodicCallback(cache.clear_expires, 1000 * 1800).start()
    return cache


cache = get_cache(DEFAULT_CACHE_ALIAS)


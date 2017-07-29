import sys
import cPickle
from datetime import datetime

from . import logger, util


class ExpirableValue:
    def __init__(self, value, max_age=None):
        self.value = value
        self.created_at = datetime.utcnow()
        self.max_age = max_age

    def __repr__(self):
        return '<ExpirableValue %s>' % repr(self.__dict__)

    def is_expired(self):
        if not self.max_age:
            return False

        now = datetime.utcnow()
        age = now - self.created_at
        return age.total_seconds() > self.max_age


class MemoryCache:
    """
    Cache implementation stored in memory
    """
    def __init__(self, prefix=u''):
        self.cache = {}
        self.prefix = prefix + u'_'
        self.cached = CacheDecorator(self)

    def _make_key(self, k):
        return self.prefix + unicode(k)

    def get_or_put(self, key, val_fun, max_age=None):
        value = self.get(key)
        if value is None:
            return self.put(key, val_fun(), max_age)
        return value

    def get(self, key):
        key = self._make_key(key)
        value = self.cache.get(key, None)
        if value is None or value.is_expired():
            return None
        else:
            return value.value

    def put(self, key, value, max_age=None):
        self.cache[self._make_key(key)] = ExpirableValue(value, max_age)
        return value

    def delete(self, key):
        self.cache.pop(self._make_key(key), None)

    def delete_all(self):
        self.cache = {}

    def keys(self):
        return [key.replace(self.prefix, '', 1)
                for key in self.cache.keys()
                if key.startswith(self.prefix)]


class RedisCache:
    """
    Redis based cache implementation.
    """
    def __init__(self, con, prefix=u'', debug=False):
        """
        prefix: specify a cache key prefix. Useful for shared
            caches (e.g. redis)
        debug: if True additional debug information is logged
        """
        self.con = con
        self.prefix = prefix + u'_'
        self.debug = debug
        self.cached = CacheDecorator(self)

    @util.wrap_time("Cache.get_or_put")
    def get_or_put(self, key, val_fun, max_age=None):
        """"
        Returns the cached value for key if found.
        val_fun is called to compute and cache the value if not found.

        max_age (in seconds) can be used to set an expiration on
        the cached value
        """
        res = self.get(key)
        if res is None:
            return self.put(key, val_fun(), max_age)
        else:
            return res

    @util.wrap_time("Cache.get")
    def get(self, key):
        "Returns the cached value for key or None if not found in cache."
        key = self._make_key(key)
        with util.timeit("Cache.con.get"):
            value = self.con.get(key)

        if value is None:
            return None

        if self.debug:
            logger.debug("Cache.sizeof %s" % sys.getsizeof(value))
        with util.timeit("Cache.pickle_load"):
            return cPickle.loads(value)

    def put(self, key, value, max_age=None):
        "stores the specified value in the cache. Can be retrieved by key."
        if max_age:
            age_in_ms = int(round(1000 * max_age))
        else:
            age_in_ms = None
        serialized = cPickle.dumps(value)
        self.con.set(self._make_key(key), serialized, px=age_in_ms)
        return value

    def delete(self, key):
        "delete the specified key in the cache if it exists."
        self.con.delete(self._make_key(key))

    def delete_all(self):
        "delete all keys in the cache"
        matches = self.con.keys(self.prefix + '*')
        if matches:
            self.con.delete(*matches)

    def keys(self):
        "returns keys for all items in the cache"
        keys = self.con.keys(self.prefix + '*')
        return map(lambda k: k.replace(self.prefix, '', 1), keys)

    def _make_key(self, key):
        return self.prefix + unicode(key)


class NoneCache:
    """
    Cache implementation that does no caching.
    This is useful in test environments where each tesst should be
    able to run independently.
    """
    def __init__(self):
        self.cached = CacheDecorator(self)

    def get(self, key):
        return None

    def put(self, key, value):
        return value

    def get_or_put(self, key, val_fun, max_age=None):
        return val_fun()

    def delete(self, key):
        pass

    def delete_all(self):
        pass

    def keys(self):
        return []


class CacheDecorator(object):
    def __init__(self, cache):
        self.cache = cache

    def __call__(self, timeout):
        "timeout: in seconds"
        def wrap(f):
            def decorated(*args, **kwargs):
                key = str(f.__class__) + '.' + str(f.__name__)
                return self.cache.get_or_put(
                    key,
                    lambda: f(*args, **kwargs),
                    max_age=timeout)
            return decorated
        return wrap

import sys
import cPickle
from datetime import datetime

import logging
import util


class _Value:
    def __init__(self, value):
        self.value = value
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return '<_Value %s>' % repr(self.__dict__)


class _BaseCache(object):
    def __init__(self, prefix='', debug=False):
        """
        prefix: specify a cache key prefix. Useful for shared
            caches (e.g. redis)
        debug: if True additional debug information is logged
        """
        self.prefix = prefix
        self.debug = debug
        self.cached = CacheDecorator(self)

    @util.wrap_time("Cache.get")
    def get(self, key):
        "Returns the cached value for key or None if not found in cache."
        val = self._get(key)
        return val if not val else val.value

    @util.wrap_time("Cache.get_or_put")
    def get_or_put(self, key, val_fun, max_age=None):
        """"
        Returns the cached value for key if found.
        valu_fun is called to compute and cache the value if not found.

        max_age (in seconds) can be used to set an expiration on
        the cached value
        """
        val = self._get(key)
        if not val:
            return self.put(key, val_fun())
        elif val and max_age:
            now = datetime.utcnow()
            age = now - val.created_at
            if age.total_seconds() > max_age:
                return self.put(key, val_fun())
            else:
                return val.value
        else:
            return val.value

    def put(self, key, value):
        "stores the specified value in the cache. Can be retrieved by key."
        value = _Value(value)
        serialized = self._serialize(value)
        self._do_put(self._make_key(key), serialized)
        return value.value

    def delete(self, key):
        "delete the specified key in the cache if it exists."
        self._do_delete(self._make_key(key))

    def delete_all(self):
        "delete all keys in the cache"
        raise NotImplementedError()

    def keys(self):
        "returns keys for all items in the cache"
        return map(self._to_short_key, self._get_keys())

    @util.wrap_time("Cache._get")
    def _get(self, key):
        with util.timeit("Cache.con.get"):
            v = self._do_get(self._make_key(key))

        if v is None:
            return None
        if self.debug:
            logging.debug("Cache.sizeof %s" % sys.getsizeof(v))
        with util.timeit("Cache.pickle_load"):
            return self._deserialize(v)

    def _do_get(self, full_key):
        raise NotImplementedError()

    def _do_put(self, full_key, serialized_value):
        raise NotImplementedError()

    def _do_delete(self, full_key):
        raise NotImplementedError()

    @util.wrap_time('Cache._make_key')
    def _make_key(self, key):
        return u'{}_{}'.format(self.prefix,
                               self._serialize(key))

    def _to_short_key(self, key):
        return self._deserialize(key.replace('{}_'.format(self.prefix), '', 1))

    @util.wrap_time('Cache._serialize')
    def _serialize(self, key):
        return key

    @util.wrap_time('Cache._deserialize')
    def _deserialize(self, value):
        return value


class MemoryCache(_BaseCache):
    """
    Cache implementation stored in memory
    """
    def __init__(self, prefix='', debug=False):
        self.cache = {}
        super(MemoryCache, self).__init__(prefix, debug)

    def _do_get(self, full_key):
        return self.cache.get(full_key)

    def _do_put(self, full_key, serialized_value):
        self.cache[full_key] = serialized_value

    def _do_delete(self, full_key):
        self.cache.pop(full_key, None)

    def delete_all(self):
        for key in self.cache.keys():
            if key.startswith(self.prefix):
                self._do_delete(key)

    def _get_keys(self):
        return self.cache.keys()


class RedisCache(_BaseCache):
    """
    Redis based cache implementation.
    """
    def __init__(self, con, prefix='', debug=False):
        self.con = con
        super(RedisCache, self).__init__(prefix, debug)

    def _serialize(self, key):
        return cPickle.dumps(key)

    def _deserialize(self, value):
        return cPickle.loads(value)

    def _do_get(self, full_key):
        return self.con.get(full_key)

    def _do_put(self, full_key, serialized_value):
        self.con.set(full_key, serialized_value)

    def _do_delete(self, full_key):
        self.con.delete(full_key)

    def delete_all(self):
        matches = self.con.keys(self.prefix + '*')
        if matches:
            self.con.delete(*matches)

    def _get_keys(self):
        return [k for k in self.con.keys(self.prefix + '*')]


class NoneCache:
    """
    Cache implementation that does no caching.
    This is useful in test environments where each tesst should be
    able to run independently.
    """
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

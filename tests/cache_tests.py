import time
from datetime import datetime

from context import assert_is_none, assert_equals

from crust import cache


def test_none_cache():
    c = cache.NoneCache()
    assert_is_none(c.get("foo"))
    c.put("foo", 1)
    assert_is_none(c.get("foo"))
    assert_equals(2, c.get_or_put("foo", lambda: 1 + 1))
    c.delete('a')
    c.delete_all()
    assert_equals([], c.keys())


class BaseCacheTest:
    def test_missing_key(self):
        assert_is_none(self.cache.get('bar'))

    def test_put(self):
        value = {'foo': 'bar', 'created_at': datetime.now()}
        assert_equals(value, self.cache.put('bar', value))
        assert_equals(value, self.cache.get('bar'))

    def test_delete(self):
        self.cache.delete('missing-key')
        self.cache.put('foo', 'bar')
        assert_equals('bar', self.cache.get('foo'))
        self.cache.delete('foo')
        assert_is_none(self.cache.get('bar'))

    def test_get_or_put(self):
        assert_equals(2, self.cache.get_or_put('bar', lambda: 1 + 1))
        assert_equals(2, self.cache.get('bar'))
        assert_equals(2, self.cache.get_or_put('bar', lambda: 4))
        assert_equals(2, self.cache.get('bar'))

    def test_delete_all(self):
        self.cache.put('bar', 2)
        assert_equals(2, self.cache.get('bar'))
        self.cache.delete_all()
        assert_is_none(self.cache.get('bar'))

    def test_keys(self):
        self.cache.put('bar', 2)
        assert_equals(['bar'], self.cache.keys())
        self.cache.delete('bar')
        assert_equals([], self.cache.keys())

    def test_max_age(self):
        self.cache.put('bar', 1, .001)
        time.sleep(.01)
        assert_equals(2, self.cache.get_or_put('bar', lambda: 2, .001))

    def test_complex_key(self):
        key = {"foo": "bar"}
        self.cache.put(key, 1)
        assert_equals(1, self.cache.get(key))

    def test_cached_decorator(self):
        class CachedTester:
            def __init__(self):
                self.i = 0

            @self.cache.cached(timeout=.1)
            def cached(self):
                self.i = self.i + 1
                return self.i

        tester = CachedTester()

        assert_equals(1, tester.cached())
        assert_equals(1, tester.cached())
        time.sleep(.15)
        assert_equals(2, tester.cached())


class TestMemoryCache(BaseCacheTest):
    def setUp(self):
        self.cache = cache.MemoryCache(prefix='cache_test')


class TestRedisCache(BaseCacheTest):
    def setUp(self):
        try:
            import redis as redislib
            self.redis = redislib.StrictRedis()
            self.redis.flushall()
            self.cache = cache.RedisCache(self.redis, prefix='cache_test')
        except ImportError:
            print "Please install redis to test Redis cache implemntation"
            self.redis = None
            self.cache = cache.MemoryCache()

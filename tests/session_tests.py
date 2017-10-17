from context import (assert_equals, assert_false, assert_is_not_none,
                     assert_true, raises)

from crust import session
import web


class RedisTester:
    def __init__(self, db=None):
        self.db = db or {}
        self.expires = {}

    def get(self, key):
        return self.db.get(key, None)

    def expire(self, key, timeout):
        self.expires[key] = timeout

    def set(self, key, value):
        self.db[key] = value

    def delete(self, key):
        self.db.pop(key, None)
        self.expires.pop(key, None)

TWO_ENCODED = 'STIKLg==\n'


def test_redis_get():
    redis = RedisTester({'sessions_a': TWO_ENCODED})
    sessions = session.RedisStore(redis, timeout=20)
    assert_equals(2, sessions['a'])


@raises(KeyError)
def test_redis_get_key_not_found():
    redis = RedisTester()
    sessions = session.RedisStore(redis, timeout=20)

    sessions['a']


def test_redis_set():
    redis = RedisTester()
    sessions = session.RedisStore(redis, timeout=20)

    sessions['foo'] = 2
    assert_is_not_none(redis.db['sessions_foo'])
    assert_equals(TWO_ENCODED, redis.db['sessions_foo'])
    assert_equals(20, redis.expires['sessions_foo'])


def test_redis_delete():
    redis = RedisTester({'sessions_a': TWO_ENCODED})
    sessions = session.RedisStore(redis, timeout=20)

    del sessions['a']
    assert_equals({}, redis.db)


def test_in_():
    redis = RedisTester({'sessions_a': TWO_ENCODED})
    sessions = session.RedisStore(redis, timeout=20)

    assert_true('a' in sessions)
    assert_false('b' in sessions)


def test_flash():
    app = web.application({}, {})
    store = web.session.DiskStore('sessions')
    flash = session.Flash(session.Session(app, store))
    assert_equals([], flash.messages('test'))

    # reset web.ctx flash. This simulates processing a new request.
    web.ctx.pop('flash', None)
    flash.add('test', 'foo')
    flash.add('error', 'biz')
    flash.now('error', 'baz')

    assert_equals(['foo'], flash.session.flash['test'])
    assert_equals(['biz'], flash.session.flash['error'])
    assert_equals(['baz'], web.ctx.flash_now['error'])

    assert_equals(['foo'], flash.messages('test'))
    assert_equals(['biz', 'baz'], flash.messages('error'))

    # reset web.ctx flash. This simulates processing a new request.
    web.ctx.pop('flash', None)
    flash.now('success', 'logged out')
    assert_equals(['logged out'], flash.messages('success'))
    # make sure it stays in the context even though it's a now message
    assert_equals(['logged out'], flash.messages('success'))
    # make sure it's not stored in the session
    assert_equals([], flash.session.flash['success'])

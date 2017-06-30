import web

from collections import defaultdict


class RedisStore(web.session.Store):
    def __init__(self, redis, key_prefix="sessions_", timeout=None):
        self.redis = redis
        self.key_prefix = key_prefix
        self.timeout = timeout or web.webapi.config.session_parameters.timeout

    def _make_key(self, key):
        return self.key_prefix + key

    def _update_expire(self, fullkey):
        self.redis.expire(fullkey, self.timeout)

    def __contains__(self, key):
        return bool(self.redis.get(self._make_key(key)))

    def __getitem__(self, key):
        key = self._make_key(key)
        data = self.redis.get(key)
        if data:
            self._update_expire(key)
            return self.decode(data)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        key = self._make_key(key)
        self.redis.set(key, self.encode(value))
        self._update_expire(key)

    def __delitem__(self, key):
        self.redis.delete(self._make_key(key))

    def cleanup(self, timeout):
        # redis handles this
        pass


def Session(app, session_store, initializer=None):
    initializer = initializer or {'flash': defaultdict(list),
                                  'user_id': None}

    if web.config.get('_session') is None:
        session = web.session.Session(app, session_store, initializer)
        web.config._session = session
    else:
        session = web.config._session
    return session


class Flash:
    def __init__(self, session):
        self.session = session

    def add(self, group, *messages):
        for message in messages:
            self.session.flash[group].append(message)

    def messages(self, group=None):
        if not hasattr(web.ctx, 'flash'):
            web.ctx.flash = self.session.flash
            self.session.flash = defaultdict(list)
        if group:
            return web.ctx.flash.get(group, [])
        else:
            return web.ctx.flash

    def reset(self):
        for k in self.session.flash.keys():
            self.session.flash.pop(k)

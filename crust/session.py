import web


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

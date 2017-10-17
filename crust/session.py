import web

from collections import defaultdict


class RedisStore(web.session.Store):
    """
    Redis backed web session Store
    Usage:
        >>> import redis
        >>> r = redis.StrictRedis()
        >>> from crust import session
        >>> session_store = session.RedisStore(redis)
        >>> import web
        >>> app = web.application({}, globals())
        >>> session = web.session.Session(app, session_store)
    """
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
    """
    Wrapper for allowing session store to be reloaded in dev environment.
    Usage:
        >>> from crust import session as sessionlib
        >>> import web
        >>> app = web.application({}, globals())
        >>> session_store = web.session.DiskStore('sessions')
        >>> session = sessionlib.Session(app, session_store)
    """
    initializer = initializer or {'flash': defaultdict(list),
                                  'user_id': None}

    if web.config.get('_session') is None:
        session = web.session.Session(app, session_store, initializer)
        web.config._session = session
    else:
        session = web.config._session
    return session


class Flash:
    """
    Flash message handler.
    Usage:
        >>> import web
        >>> app = web.application({}, globals())
        >>> from crust import session as sessionLib
        >>> session_store = web.session.DiskStore('sessions')
        >>> session = sessionLib.Session(app, session_store)
        >>> flash = sessionLib.Flash(session)
        >>> flash.add('success', 'User updated.')
        >>> for m in flash.messages('success'):
        ...     print m
        User updated.
    """
    def __init__(self, session):
        self.session = session

    def _init_flash(self, force=False):
        if not hasattr(self.session, 'flash') or force:
            self.session.flash = defaultdict(list)

    def add(self, group, *messages):
        """
        Add a flash message
        param: group - message group
        param: *messages - list of messages to be stored with group
        """
        self._init_flash()
        for message in messages:
            self.session.flash[group].append(message)

    def now(self, group, *messages):
        """
        Add flash messages for current request only. Won't be stored
        in session or carried over between requests.
        param: group - message group
        param: *messages - list of messages to be stored with group
        """
        if 'flash_now' not in web.ctx:
            web.ctx.flash_now = defaultdict(list)

        for message in messages:
            web.ctx.flash_now[group].append(message)

    def messages(self, group):
        """
        Returns list of messages with specified group
        param: group - name of group containing messages.
        """
        self._init_flash()
        if not hasattr(web.ctx, 'flash'):
            web.ctx.flash = self.session.flash

            # Add any now messages into the contextually stored flash
            for now_group, messages in web.ctx.pop('flash_now', {}).items():
                web.ctx.flash[now_group].extend(messages)

            self._init_flash(True)
        if group:
            return web.ctx.flash.get(group, [])
        else:
            return web.ctx.flash

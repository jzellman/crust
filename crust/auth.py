from uuid import uuid4

import web


def current_user_builder(session, id_field, user_finder):
    def current_user(reload=False):
        user_id = getattr(session, id_field, None)
        if not user_id:
            return None
        if 'user' in web.ctx and not reload:
            return web.ctx.user
        else:
            web.ctx.user = user_finder(user_id)
            return web.ctx.user
    return current_user


def AuthorizationProcessor(session, user_field="user_id", require_login=None):
    def auth_app_processor(handle):
        path = web.ctx.path
        if require_login and require_login(path):
            uri = web.ctx.environ.get('REQUEST_URI', path)
            session.back = uri
        user_id = session.get(user_field, None)
        if user_id:
            setattr(web.ctx, user_field, user_id)
        return handle()
    return auth_app_processor


class Protector:
    """
    Contains a set of common decorators useful for action level authorization.

    Usage:
        >>> import web
        >>> def current_user():
        ...     return db.load_some_user()
        ...
        >>> session = web.session.Session(app, session_store,
        ...     initializer={'user_id': None})
        >>> from crust import Protector
        >>> protect = Protector(session, current_user)
        >>> template_funs = { 'csrf_token': protect.csrf_token }
        >>> render = web.template.render('templates/', globals=template_funs)
        >>> class account:
        ...     @protect.login_required
        ...     def GET(self):
        ...         pass

    Then in the account form template

    <form method="POST">
        <input type="hidden" name="csrf-token" value="$csrf_token()">
    </form>
    """

    def __init__(self, session, user_loader, **kwargs):
        self.session = session
        self.user_loader = user_loader
        self.user_field = kwargs.get("user_field", "user_id")
        self.login_path = kwargs.get("login_path", "/login")

    def build_auth_processor(self, require_login):
        """
        returns an authorization processor which can be used
        for for authorizing URL paths.

        Usage:
            >>> session = web.session.Session(app, session_store,
            ...     initializer={"user_id": None})
            >>> app = web.application(urls, globals())
            >>> def current_user():
            ...    if session.user_id:
            ...        # load user
            ...        return load_user
            ...    else:
            ...        return None
            >>> def require_login_for_account(path):
            ...    return path.startswith("/account")
            >>> protector = Protector(session, curent_user)
            >>> app.add_processor(
            ...     protector.build_auth_processor(require_login))

        This will cause authorization for any URL starting with "/account"
        """
        def auth_app_processor(handle):
            path = web.ctx.path
            if require_login and require_login(path):
                self._verify_session_user()
            return handle()
        return auth_app_processor

    def login_required(self, f):
        def decorated(*args, **kwargs):
            self._verify_session_user()
            return f(*args, **kwargs)
        return decorated

    def admin_required(self, f):
        def decorated(*args, **kwargs):
            self._verify_session_user(web.notfound)
            user = self.user_loader()
            if not user.is_admin:
                raise web.notfound()
            return f(*args, **kwargs)
        return decorated

    def _verify_session_user(self, redirect=None):
        if not self.session.get(self.user_field, None):
            self.session.back = web.ctx.path
            if redirect:
                raise redirect()
            else:
                raise web.seeother(self.login_path)

    def csrf_protected(self, f):
	"""
        decorator for preventing CSRF attacks.

        Usage:
            >>> @csrf_protected
            ... def GET(self):
            ...     #handle web.input()

        """
        def decorated(*args, **kwargs):
            inp = web.input()
            stored_token = self.session.pop('csrf_token', None)
            if ('csrf_token' not in inp or inp.csrf_token != stored_token):
                raise web.HTTPError(
                    "400 Bad request",
                    {'content-type': 'text/html'},
                    """Cross-site request forgery (CSRF) attempt (or stale browser form).
    <a href="">Back to the form</a>.""")
            return f(*args, **kwargs)
        return decorated

    def csrf_token(self):
	"""
        Used in conjunction with csrf_protected. Within your form add
        an input containing the token:
            >>> def GET(self):
            ...     return '<form method="POST">' +
            ...              '<input type="hidden" name="csrf-token" ' +
            ...              'value="$csrf_token()">' +
            ...            ' </form>'
        """
        if 'csrf_token' not in self.session:
            self.session.csrf_token = uuid4().hex
        return self.session.csrf_token

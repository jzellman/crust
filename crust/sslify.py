import web

from . import logger


def sslify(app):
    """Forces HTTPS in environments like Heroku

    Example:

        app = web.application(urls, globals())
        import sslify
        sslify.sslify(app)
    """
    app.add_processor(_ssl_handler)


def _ssl_handler(handle):
    if web.ctx.environ.get('HTTP_X_FORWARDED_PROTO', 'http') != 'https':
        url = web.ctx.home + web.ctx.fullpath
        url = url.replace("http://", "https://", 1)
        logger.info("Redirecting to %s" % (url))
        raise web.redirect(url)
    else:
        web.header('Strict-Transport-Security', 'max-age=31536000')
        return handle()

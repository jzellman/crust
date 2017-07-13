import logging
import web

import util


def _time_header(time):
    web.header('X-Request-Time', time)


def time_request(handler):
    """
    Displays time it took to process a request.

    Usage:
        add.add_processor(time_request)
    """
    with util.timeit('Request Time %s' % web.ctx.path, _time_header):
        return handler()


def log_bad_requests(user_id_fun=None):
    """
    logs all 4xx and 5xx errors using logger library.

    Usage:
        app.add_processor(web.unloadhook(
            log_bad_requests(lambda: current_user()))
    """
    def wrapped():
        status = web.ctx.status
        if status and (status.startswith("4") or status.startswith("5")):
            user_id = user_id_fun() if user_id_fun else None
            attrs = [('code', status[0:3]),
                     ('method', web.ctx.method),
                     ('user_id', user_id),
                     ('path', web.ctx.path),
                     ('query', web.ctx.query)]
            details = " ".join("%s=%s" % (k, v) for k, v in attrs)
            logging.error(details)
    return wrapped

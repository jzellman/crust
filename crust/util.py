import logging
import time
from contextlib import contextmanager


@contextmanager
def timeit(label=""):
    start = time.time()
    yield
    end = time.time()
    logging.info('%s : %s' % (round(end-start, 2), str(label)))


def wrap_time(label):
    def wrap(f):
        def decorated(*args, **kwargs):
            with timeit("%s -- %s" % (label, locals())):
                return f(*args, **kwargs)
        return decorated
    return wrap


def safedatefmt(d, fmt=None):
    fmt = fmt or "%m/%d/%y %H:%M %p"
    if d:
        return d.strftime(fmt)
    else:
        return d


def boolfmt(b, yes="Yes", no="No"):
    return yes if b else no

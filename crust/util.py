import logging
import time
from contextlib import contextmanager


@contextmanager
def timeit(label=""):
    start = time.time()
    yield
    end = time.time()
    logging.debug('%.3f : %s' % (round(end-start, 3), str(label)))


def wrap_time(label):
    def wrap(f):
        def decorated(*args, **kwargs):
            with timeit(label):
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


def first(lst, default=None):
    "Returns first element of a list or default"
    try:
        return lst[0]
    except IndexError:
        return default

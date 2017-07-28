import functools
import time
from contextlib import contextmanager

from . import logger


@contextmanager
def timeit(label="", callback=None):
    start = time.time()
    yield
    delta = time.time() - start
    logger.debug('%.3f : %s' % (round(delta, 3), str(label)))
    if callback:
        callback(delta)


def wrap_time(label):
    def wrap(f):
        @functools.wraps(f)
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


def partition(fun, lst):
    " Returns 2 lists, list 1 where fun is True, list 2 where fun is False"
    match, nomatch = [], []
    for el in lst:
        if fun(el):
            match.append(el)
        else:
            nomatch.append(el)
    return match, nomatch

import datetime

from context import assert_equals

from crust import util


def test_safedatefmt():
    assert_equals(None, util.safedatefmt(None))
    assert_equals("", util.safedatefmt(""))
    d = datetime.datetime(2016, 1, 2, 12, 24)
    assert_equals("01/02/16 12:24 PM", util.safedatefmt(d))
    assert_equals("01/02/16", util.safedatefmt(d, fmt="%m/%d/%y"))


def test_boolfmt():
    assert_equals("No", util.boolfmt(None))
    assert_equals("No", util.boolfmt(False))
    assert_equals("No", util.boolfmt(""))
    assert_equals("Yes", util.boolfmt(True))
    assert_equals("Yes", util.boolfmt(1))
    assert_equals("Hell Yeah",
                  util.boolfmt(True, yes="Hell Yeah", no="Hell No"))
    assert_equals("Hell No",
                  util.boolfmt(False, yes="Hell Yeah", no="Hell No"))


def test_timeit():
    with util.timeit():
        range(5)


def test_wrap_time():
    @util.wrap_time("hello")
    def test():
        range(5)
    test()


def test_first():
    assert_equals(1, util.first([1, 2, 3]))
    assert_equals(0, util.first(xrange(3)))
    assert_equals('default', util.first([], 'default'))
    assert_equals(None, util.first([]))

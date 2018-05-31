from .context import assert_equals, assert_true, assert_false

from crust import SimpleCryptor, Bcryptor


def test_simple():
    c = SimpleCryptor()
    assert_equals("foo", c.crypt('foo'))
    assert_crypt(c)


def test_bcrypt():
    c = Bcryptor()
    assert_crypt(c)


def assert_crypt(c):
    assert_true(c.is_crypted('foo', c.crypt('foo')))
    assert_false(c.is_crypted('foo', c.crypt('bar')))

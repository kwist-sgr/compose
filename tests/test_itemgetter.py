import re
import pytest
import compose as cp

from uuid import uuid4
from unittest.mock import MagicMock

from .base import sentinel


def test_arg_required():
    with pytest.raises(TypeError, match='itemgetter expected 1 argument, got 0'):
        cp.IG()


def test_index():
    f = cp.IG(4)
    v = sentinel.batch('a0 a1 a2 a3 a4 a5')
    assert f(v) is v.a4


def test_index_error_signle():
    f = cp.IG(14)
    with pytest.raises(IndexError, match='tuple index out of range'):
        f(sentinel.batch('a0 a1 a2 a3 a4 a5'))


def test_index_error_multi():
    f = cp.IG(1, 2, 14)
    with pytest.raises(IndexError, match='tuple index out of range'):
        f(sentinel.batch('a0 a1 a2 a3 a4 a5'))


def test_key():
    f = cp.IG('value')
    value = sentinel['value']
    assert f({'value': value}) is value


def test_key_error():
    key = str(uuid4())
    f = cp.IG(key)
    with pytest.raises(KeyError, match=re.escape(f"'{key}'")):
        f({})


def test_key_error_multi():
    key = str(uuid4())
    f = cp.IG('a', 'b', key)
    with pytest.raises(KeyError, match=re.escape(f"'{key}'")):
        f({'a': 14, 'b': 'value'})


def test_key_error_deep():
    key = str(uuid4())
    f = cp.IG(f"a.b.{key}")
    with pytest.raises(cp.ComposeError) as excinfo:
        f({'a': {'b': {}}})

    assert str(excinfo.value.origin) == f"'{key}'"


def test_multi_index():
    f = cp.IG(1, 2, 4)
    v = sentinel.batch('a0 a1 a2 a3 a4 a5')
    assert f(v) == (v.a1, v.a2, v.a4)


def test_multi_key():
    f = cp.IG('b', 'a')
    v = sentinel.batch('a b')
    assert f({'a': v.a, 'b': v.b}) == (v.b, v.a)


def test_deep_key():
    f = cp.IG('meta.info.value')
    value = sentinel['value']
    assert f({'meta': {'info': {'value': value}}}) is value


def test_key_compose_multi():
    assert isinstance(cp.IG('a', 'b', 'c'), cp.IG)


def test_key_compose_single():
    assert isinstance(cp.IG('a'), cp.IG)


def test_key_compose_deep():
    r = cp.IG('a.b.c')
    assert isinstance(r, cp.Compose)
    assert len(r.stack) == 3

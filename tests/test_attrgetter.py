import pytest
import compose as cp

from unittest.mock import MagicMock

from .base import sentinel


def test_arg_required():
    # python 3.7  : attrgetter expected 1 arguments, got 0
    # python 3.8+ : attrgetter expected 1 argument, got 0
    with pytest.raises(TypeError, match='attrgetter expected 1 arguments?, got 0'):
        cp.AG()


def test_name_single():
    f = cp.AG('b3')
    v = sentinel.batch('b0 b1 b2 b3 b4 b5')
    assert f(v) is v.b3


def test_name_multi():
    f = cp.AG('b3', 'b0', 'b4')
    v = sentinel.batch('b0 b1 b2 b3 b4 b5')
    assert f(v) == (v.b3, v.b0, v.b4)


def test_name_deep():
    item = MagicMock(name='item')
    item.a.b.id = uid = sentinel['uid']
    f = cp.AG('a.b.id')
    assert f(item) is uid


def test_name_mixed():
    v = sentinel.batch('c y value')
    f = cp.AG('a.b.c', 'value', 'x.y')

    item = MagicMock(name='item')
    item.a.b.c = v.c
    item.x.y = v.y
    item.value = v.value
    assert f(item) == (v.c, v.value, v.y)

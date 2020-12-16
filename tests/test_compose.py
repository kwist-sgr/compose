import re
import pickle
import pytest
import compose as cp

from uuid import uuid4
from unittest.mock import patch, MagicMock, Mock

from .base import sentinel


def test_create_other_other():
    a, b = MagicMock(name='a', spec=cp.C), MagicMock(name='b', spec=cp.C)
    c = cp.Compose.pipeline(a, b)
    assert isinstance(c, cp.Compose)
    assert c.stack == (a, b)


def test_create_compose_other():
    v = {x: MagicMock(name=x, spec=cp.C) for x in 'abxy'}
    z = cp.Compose(v['a'], v['b'], v['y'])
    c = cp.Compose.pipeline(z, v['x'])
    assert isinstance(c, cp.Compose)
    assert c.stack == (v['a'], v['b'], v['y'], v['x'])


def test_create_other_compose():
    v = {x: MagicMock(name=x, spec=cp.C) for x in 'abxy'}
    z = cp.Compose(v['a'], v['b'], v['y'])
    c = cp.Compose.pipeline(v['x'], z)
    assert isinstance(c, cp.Compose)
    assert c.stack == (v['x'], v['a'], v['b'], v['y'])


@patch('compose.Compose.__lshift__')
def test_lshift(mock_shift):
    a, b = MagicMock(name='a', spec=cp.C), MagicMock(name='b', spec=cp.C)
    c = cp.Compose.pipeline(a, b)
    mock_shift.return_value = shift = sentinel['shift']
    other = sentinel['other']
    assert c << other is shift
    mock_shift.assert_called_once_with(other)


def test_compose():
    v = {x: MagicMock(name=x, spec=cp.C) for x in 'xyz'}
    c = cp.Compose.pipeline(v['x'], v['y'])
    new = c << v['z']
    assert isinstance(new, cp.Compose)
    assert new.stack == tuple(v.values())


def test_create_empty():
    with pytest.raises(TypeError, match='Compose expected at least 1 argument, got 0'):
        cp.Compose()


def test_compose_callable():

    class Callable:
        _repr = str(uuid4())

        def __repr__(self):
            return self._repr

        def __call__(self):
            pass

    message = "All passed items must be callable, got {} instead"
    with pytest.raises(ValueError, match=re.escape(message)):
        cp.Compose(cp.Int, Callable(), {})


def test_compose_non_callable():

    class NotCallable:
        _repr = str(uuid4())

        def __repr__(self):
            return self._repr

    item = NotCallable()
    message = f"All passed items must be callable, got {item!r} instead"
    with pytest.raises(ValueError, match=re.escape(message)):
        cp.Compose(cp.Int, item, {})


@patch('compose.reversed')
@patch('compose.flip')
@patch('compose.reduce')
def test_call(mock_reduce, mock_flip, mock_reversed):
    mock_reduce.return_value = reduce_ = sentinel['reduce']
    mock_reversed.return_value = rev = sentinel['reversed']
    mock_flip.return_value = flip = sentinel['flip']
    a, b = MagicMock(name='a', spec=cp.C), MagicMock(name='b', spec=cp.C)
    arg = sentinel['arg']
    c = cp.Compose(a, b)
    assert c(arg) is reduce_
    mock_flip.assert_called_once_with(cp.safe_apply)
    mock_reversed.assert_called_once_with(c.stack)
    mock_reduce.assert_called_once_with(flip, rev, arg)


def test_compose_call():
    f = cp.Compose(cp.Sum, cp.Map(int), cp.Str)
    assert repr(f) == "<Compose: sum,map(int),str>"
    assert f(763) == 16


def test_call_with_signle_func():
    c = cp.Compose(cp.Int)
    assert c('124') == 124


def test_call_result():
    value = sentinel.batch('x y z arg')
    x = Mock(name='x', spec=cp.C, return_value=value.x)
    y = Mock(name='y', spec=cp.C, return_value=value.y)
    z = Mock(name='z', spec=cp.C, return_value=value.z)

    c = cp.Compose(x, y, z)
    # `x` called last
    assert c(value.arg) is value.x
    z.assert_called_once_with(value.arg)
    y.assert_called_once_with(value.z)
    x.assert_called_once_with(value.y)


def test_eq():
    a = cp.Compose(int)
    b = cp.Compose(str)
    a.stack = MagicMock(name='stack.a')
    b.stack = MagicMock(name='stack.b')

    a.stack.__eq__.return_value = True
    assert a == b
    a.stack.__eq__.assert_called_once_with(b.stack)

    a.stack.reset_mock()
    a.stack.__eq__.return_value = False
    assert a != b
    a.stack.__eq__.assert_called_once_with(b.stack)


def test_eq_unsupported(subtests):
    f = cp.C(float)
    for x in ([1, 2], {1: 2}, object(), 12, '67', {12}):
        with subtests.test(repr(x)):
            assert f.__eq__(x) is NotImplemented


def test_pickle(subtests):
    c = cp.Compose(int, float, round)
    for protocol in range(2, pickle.HIGHEST_PROTOCOL):
        with subtests.test(f"protocol={protocol}"):
            assert c == pickle.loads(pickle.dumps(c, protocol))

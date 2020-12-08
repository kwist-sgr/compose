import pickle
import compose as cp

from unittest.mock import patch, Mock, MagicMock

from .base import sentinel, NamedMock


@patch('compose.C.__lshift__')
def test_lshift(mock_shift):
    mock_shift.return_value = shift = sentinel['shift']
    a = cp.C(Mock(name='func_a'))
    other = sentinel['other']
    assert a << other is shift
    mock_shift.assert_called_once_with(other)


def test_compose():
    a = cp.C(NamedMock(name='func.a'))
    b = cp.C(NamedMock(name='func.b'))
    c = a << b
    assert isinstance(c, cp.Compose)
    assert c.stack == (a, b)


def test_call():
    v = sentinel.batch('arg res')
    func = MagicMock(name='func', return_value=v.res)
    a = cp.C(func)
    assert a(v.arg) is v.res
    func.assert_called_once_with(v.arg)


def test_eq():
    func_a = NamedMock(name='func.a')
    func_a.__eq__.return_value = True
    func_b = MagicMock(name='func_b')
    a = cp.C(func_a)
    b = cp.C(func_b)
    assert a == b
    func_a.__eq__.assert_called_once_with(func_b)

    func_a.reset_mock()
    func_a.__eq__.return_value = False
    assert a != b
    func_a.__eq__.assert_called_once_with(func_b)


def test_eq_unsupported(subtests):
    f = cp.C(float)
    for x in ([1, 2], {1: 2}, object(), 12, '67', {12}):
        with subtests.test(repr(x)):
            assert f.__eq__(x) is NotImplemented


def test_pickle(subtests):
    f = cp.C(int)
    for protocol in range(2, pickle.HIGHEST_PROTOCOL):
        with subtests.test(f"protocol={protocol}"):
            assert f == pickle.loads(pickle.dumps(f, protocol))

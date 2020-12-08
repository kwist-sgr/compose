import compose as cp

from unittest.mock import patch, Mock, MagicMock

from .base import sentinel


@patch('compose.C.__lshift__')
def test_lshift(mock_shift):
    mock_shift.return_value = shift = sentinel['shift']
    a = cp.C(Mock(name='func_a'))
    other = sentinel['other']
    assert a << other is shift
    mock_shift.assert_called_once_with(other)


def test_compose():
    value = sentinel.batch('a b')
    a = cp.C(value.a)
    b = cp.C(value.b)
    c = a << b
    assert isinstance(c, cp.Compose)
    assert c.stack == (a, b)


def test_call():
    v = sentinel.batch('arg res')
    func = MagicMock(name='func', return_value=v.res)
    a = cp.C(func)
    assert a(v.arg) is v.res
    func.assert_called_once_with(v.arg)

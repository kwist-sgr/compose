from unittest.mock import patch

import compose as cp

from .base import sentinel, NamedMock


@patch('compose.partial')
def test_init(mock_partial):
    v = sentinel.batch('arg1 arg2 kwarg')
    mock_partial.return_value = func = NamedMock(name='func')
    p = cp.P(func, v.arg1, v.arg2, value=v.kwarg)
    assert p.func is func
    mock_partial.assert_called_once_with(func, v.arg1, v.arg2, value=v.kwarg)


def test_partial():
    v = [5, 1, 9, 7]
    p = cp.P(sorted, reverse=True)
    assert sorted(v) == [1, 5, 7, 9]
    assert p(v) == [9, 7, 5, 1]

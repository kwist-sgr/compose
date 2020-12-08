from unittest.mock import patch

import compose as cp

from .base import NamedMock


@patch('compose.partial')
def test_init(mock_partial):
    mock_partial.return_value = func = NamedMock(name='filter')
    mock_partial.return_value = func
    p = cp.Filter(func)
    assert p.func is func
    mock_partial.assert_called_once_with(filter, func)


def test_filter():
    v = [1, 0, 't', False, 0.0, '0', {}, {1}, ['value'], []]
    f = cp.Filter(bool)
    assert list(f(v)) == [1, 't', '0', {1}, ['value']]

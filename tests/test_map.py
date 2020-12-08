from unittest.mock import patch

import compose as cp

from .base import NamedMock


@patch('compose.partial')
def test_init(mock_partial):
    mock_partial.return_value = func = NamedMock(name='map')
    p = cp.Map(func)
    assert p.func is func
    mock_partial.assert_called_once_with(map, func)


def test_map():
    v = [1, 0, 't', False, 0.0, '0', {}, {1}, ['value'], []]
    m = cp.Map(bool)
    assert list(m(v)) == [True, False, True, False, False, True, False, True, True, False]

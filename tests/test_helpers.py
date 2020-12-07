import compose as cp

from unittest.mock import Mock

from .base import sentinel


def test_flip():
    @cp.flip
    def func(a, b):
        return [a, b]

    x, y = sentinel['x'], sentinel['y']
    assert func(x, y) == [y, x]


def test_apply():
    func = Mock(name='func')
    arg = sentinel['arg']
    cp.apply(func, arg)
    func.assert_called_once_with(arg)

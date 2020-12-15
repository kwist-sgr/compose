import re
import pytest
import compose as cp

from unittest.mock import Mock

from .base import sentinel


def test_flip():
    @cp.flip
    def func(a, b):
        return [a, b]

    x, y = sentinel['x'], sentinel['y']
    assert func(x, y) == [y, x]


def test_safe_apply():
    func = Mock(name='func')
    arg = sentinel['arg']
    cp.safe_apply(func, arg)
    func.assert_called_once_with(arg)


def test_safe_apply_error():
    exc = RuntimeError('some runtime error')
    func = Mock(name='func', side_effect=exc)
    arg = sentinel['arg']

    message = f"{func!r}({arg!r}) caused error: {exc}"
    with pytest.raises(cp.ComposeError, match=re.escape(message)) as excinfo:
        cp.safe_apply(func, arg)

    assert excinfo.value.origin is exc


def test_compose_error():
    func, arg = Mock(name='func'), Mock(name='arg')
    exc = cp.ComposeError(func, arg)
    exc.__cause__ = origin = ImportError('origin exception')

    assert exc.func is func
    assert exc.arg is arg
    assert exc.origin is origin

    # __str__
    assert str(exc) == f"{func!r}({arg!r}) caused error: {origin}"

    # __repr__
    assert repr(exc) == f"ComposeError(func={func!r}, arg={arg!r})"

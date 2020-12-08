import re
import pytest
import compose as cp

from unittest.mock import patch

from .base import sentinel


def test_shift_childs():
    assert issubclass(cp.Compose, cp.Shift), 'Compose is Shift subclass'
    assert issubclass(cp.C, cp.Shift), 'C is Shift subclass'


@patch('compose.Compose.pipeline')
def test_shift_shift(mock_pipeline):
    mock_pipeline.return_value = shift = sentinel['shift']
    a = type('A', (cp.Shift,), {})()
    b = type('B', (cp.Shift,), {})()
    assert a << b is shift
    mock_pipeline.assert_called_once_with(a, b)


def test_shift_other(subtests):
    a = type('A', (cp.Shift,), {})()
    for x in ('v1', 1, {'v': 1}, [4], {7, 0}, object()):
        message = f"unsupported operand type(s) for <<: 'A' and {x.__class__.__name__!r}"
        with subtests.test(x.__class__.__name__):
            with pytest.raises(TypeError, match=re.escape(message)):
                a << x

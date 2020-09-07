#!/usr/bin/env python
import gc
import unittest
import warnings

from collections import namedtuple
from unittest.mock import patch, Mock, MagicMock


try:
    import compose as s
except ImportError as e:
    raise RuntimeError('Compose module not found, reference tests/README.rst for instructions.') from e


# Make resource and runtime warning errors to ensure no usage of error prone patterns.
warnings.simplefilter("error", DeprecationWarning)
warnings.simplefilter("error", ResourceWarning)
warnings.simplefilter("error", RuntimeWarning)


class _SentinelObject(object):
    "A unique, named, sentinel object."
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'sentinel.{self.name}'

    def __reduce__(self):
        return f'sentinel.{self.name}'


class TestCase(unittest.TestCase):

    class _Sentinel(object):
        """Access items to return a named object, usable as a sentinel."""

        def __getitem__(self, name):
            return _SentinelObject(name)

        def __reduce__(self):
            return 'sentinel'

    sentinel = _Sentinel()

    def tearDown(self):
        # Collect garbage on tearDown. (This can print ResourceWarnings.)
        gc.collect()


class HelpersTestCase(TestCase):

    def test_flip(self):

        @s.flip
        def func(a, b):
            return [a, b]

        x, y = self.sentinel['x'], self.sentinel['y']
        self.assertListEqual(func(x, y), [y, x])

    def test_apply(self):
        func = Mock(name='func')
        arg = self.sentinel['arg']
        s.apply(func, arg)
        func.assert_called_once_with(arg)


class CompositionTestCase(TestCase):

    def test_create_other_other(self):
        a, b = self.sentinel['a'], self.sentinel['b']
        c = s.Compose(a, b)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [a, b])

    def test_create_compose_other(self):
        a, b, x, y = self.sentinel['a'], self.sentinel['b'], self.sentinel['x'], self.sentinel['y']
        z = s.Compose(a, b)
        z.stack.append(y)
        c = s.Compose(z, x)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [a, b, y, x])

    def test_create_other_compose(self):
        a, b, x, y = self.sentinel['a'], self.sentinel['b'], self.sentinel['x'], self.sentinel['y']
        z = s.Compose(a, b)
        z.stack.append(y)
        c = s.Compose(x, z)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [x, a, b, y])

    @patch('compose.Compose.__lshift__')
    def test_lshift(self, mock_shift):
        c = s.Compose(Mock(name='a'), Mock(name='b'))
        mock_shift.return_value = shift = self.sentinel['shift']
        other = self.sentinel['other']
        self.assertIs(c << other, shift)
        mock_shift.assert_called_once_with(other)

    def test_compose(self):
        Value = namedtuple('Values', 'x y z')
        value = Value._make([self.sentinel[f'value_{f}'] for f in Value._fields])

        c = s.Compose(value.x, value.y)
        new = c << value.z
        self.assertIsInstance(new, s.Compose)
        self.assertListEqual(new.stack, list(value))

    @patch('compose.reversed')
    @patch('compose.flip')
    @patch('compose.reduce')
    def test_call(self, mock_reduce, mock_flip, mock_reversed):
        mock_reduce.return_value = reduce = self.sentinel['reduce']
        mock_reversed.return_value = rev = self.sentinel['reversed']
        mock_flip.return_value = flip = self.sentinel['flip']
        a, b, arg = self.sentinel['a'], self.sentinel['b'], self.sentinel['arg']
        c = s.Compose(a, b)
        self.assertIs(c(arg), reduce)
        mock_flip.assert_called_once_with(s.apply)
        mock_reversed.assert_called_once_with(c.stack)
        mock_reduce.assert_called_once_with(flip, rev, arg)

    def test_call_result(self):
        Value = namedtuple('Values', 'x y z arg')

        value = Value._make([self.sentinel[f'value_{f}'] for f in Value._fields])
        x = Mock(name='x', return_value=value.x)
        y = Mock(name='y', return_value=value.y)
        z = Mock(name='z', return_value=value.z)

        c = s.Compose(x, y)
        c.stack.append(z)
        # `x` called last
        self.assertIs(c(value.arg), value.x)
        z.assert_called_once_with(value.arg)
        y.assert_called_once_with(value.z)
        x.assert_called_once_with(value.y)


class ComposeTestCase(TestCase):

    @patch('compose.C.__lshift__')
    def test_lshift(self, mock_shift):
        mock_shift.return_value = shift = self.sentinel['shift']
        a = s.C(Mock(name='func_a'))
        other = self.sentinel['other']
        self.assertIs(a << other, shift)
        mock_shift.assert_called_once_with(other)

    def test_compose(self):
        Value = namedtuple('Values', 'a b')
        value = Value._make([self.sentinel[f'value_{f}'] for f in Value._fields])

        a = s.C(value.a)
        b = s.C(value.b)
        c = a << b
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [a, b])


class ItemGetterTestCase(TestCase):

    def test_index(self):
        pass

    def test_name(self):
        pass

    def test_multi_index(self):
        pass

    def test_multi_name(self):
        pass


if __name__ == "__main__":
    unittest.main()

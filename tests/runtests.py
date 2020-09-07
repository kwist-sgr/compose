#!/usr/bin/env python
import gc
import unittest
import warnings

from unittest.mock import patch, Mock


try:
    import compose as s
except ImportError as e:
    raise RuntimeError(
        'Compose module not found, reference tests/README.rst for instructions.'
    ) from e


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


class HelpersTest(TestCase):

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


class ComposeTest(TestCase):

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

    @patch('compose.reduce')
    def test_compose(self, mock_reduce):
        pass

    @patch('compose.reversed')
    @patch('compose.flip')
    @patch('compose.reduce')
    def test_call(self, mock_reduce, mock_flip, mock_reversed):
        mock_reduce.return_value = reduce = self.sentinel['reduce']
        mock_flip.return_value = flip = self.sentinel['flip']
        a, b, arg = self.sentinel['a'], self.sentinel['b'], self.sentinel['arg']
        c = s.Compose(a, b)
        self.assertIs(c(arg), reduce)
        mock_flip.assert_called_once_with(s.apply)
        mock_reduce.assert_called_once_with(flip, [b, a], arg)

    def test_call_result(self):

        def a():
            pass

        def b():
            pass

        c = s.Compose(a, b)


if __name__ == "__main__":
    unittest.main()

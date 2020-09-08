#!/usr/bin/env python
import gc
import unittest
import warnings

from uuid import uuid4
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

    def create_sentinels(self, names):
        Row = namedtuple('Row', names)
        return Row._make(self.sentinel[f'value_{f}'] for f in Row._fields)

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
        v = self.create_sentinels('a b')
        c = s.Compose(*v)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [v.a, v.b])

    def test_create_compose_other(self):
        v = self.create_sentinels('a b x y')
        z = s.Compose(v.a, v.b)
        z.stack.append(v.y)
        c = s.Compose(z, v.x)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [v.a, v.b, v.y, v.x])

    def test_create_other_compose(self):
        v = self.create_sentinels('a b x y')
        z = s.Compose(v.a, v.b)
        z.stack.append(v.y)
        c = s.Compose(v.x, z)
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [v.x, v.a, v.b, v.y])

    @patch('compose.Compose.__lshift__')
    def test_lshift(self, mock_shift):
        c = s.Compose(Mock(name='a'), Mock(name='b'))
        mock_shift.return_value = shift = self.sentinel['shift']
        other = self.sentinel['other']
        self.assertIs(c << other, shift)
        mock_shift.assert_called_once_with(other)

    def test_compose(self):
        value = self.create_sentinels('x y z')
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
        v = self.create_sentinels('a b arg')
        c = s.Compose(v.a, v.b)
        self.assertIs(c(v.arg), reduce)
        mock_flip.assert_called_once_with(s.apply)
        mock_reversed.assert_called_once_with(c.stack)
        mock_reduce.assert_called_once_with(flip, rev, v.arg)

    def test_call_result(self):
        value = self.create_sentinels('x y z arg')
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
        value = self.create_sentinels('a b')
        a = s.C(value.a)
        b = s.C(value.b)
        c = a << b
        self.assertIsInstance(c, s.Compose)
        self.assertListEqual(c.stack, [a, b])


class AttrGetterTestCase(TestCase):

    def test_arg_required(self):
        with self.assertRaises(TypeError) as cm:
            s.AG()
        self.assertEqual(str(cm.exception), 'attrgetter expected 1 argument, got 0')

    def test_name_single(self):
        f = s.AG('b3')
        v = self.create_sentinels('b0 b1 b2 b3 b4 b5')
        self.assertIs(f(v), v.b3)

    def test_name_multi(self):
        f = s.AG('b3', 'b0', 'b4')
        v = self.create_sentinels('b0 b1 b2 b3 b4 b5')
        self.assertTupleEqual(f(v), (v.b3, v.b0, v.b4))

    def test_name_deep(self):
        item = MagicMock(name='item')
        item.a.b.id = uid = self.sentinel['uid']
        f = s.AG('a.b.id')
        self.assertIs(f(item), uid)

    def test_name_mixed(self):
        v = self.create_sentinels('c y value')
        f = s.AG('a.b.c', 'value', 'x.y')

        item = MagicMock(name='item')
        item.a.b.c = v.c
        item.x.y = v.y
        item.value = v.value
        self.assertTupleEqual(f(item), (v.c, v.value, v.y))


class ItemGetterTestCase(TestCase):

    def test_arg_required(self):
        with self.assertRaises(TypeError) as cm:
            s.IG()
        self.assertEqual(str(cm.exception), 'itemgetter expected 1 argument, got 0')

    def test_index(self):
        f = s.IG(4)
        v = self.create_sentinels('a0 a1 a2 a3 a4 a5')
        self.assertIs(f(v), v.a4)

    def test_index_error_signle(self):
        f = s.IG(14)
        with self.assertRaises(IndexError) as cm:
            f(self.create_sentinels('a0 a1 a2 a3 a4 a5'))
        self.assertEqual(str(cm.exception), 'tuple index out of range')

    def test_index_error_multi(self):
        f = s.IG(1, 2, 14)
        with self.subTest('multi'):
            with self.assertRaises(IndexError) as cm:
                f(self.create_sentinels('a0 a1 a2 a3 a4 a5'))
            self.assertEqual(str(cm.exception), 'tuple index out of range')

    def test_key(self):
        f = s.IG('value')
        value = self.sentinel['value']
        self.assertIs(f({'value': value}), value)

    def test_key_error(self):
        key = str(uuid4())
        f = s.IG(key)
        with self.assertRaises(KeyError) as cm:
            f({})
        self.assertEqual(str(cm.exception), f"'{key}'")

    def test_key_error_multi(self):
        key = str(uuid4())
        f = s.IG('a', 'b', key)
        with self.assertRaises(KeyError) as cm:
            f({'a': 14, 'b': 'value'})
        self.assertEqual(str(cm.exception), f"'{key}'")

    def test_key_error_deep(self):
        key = str(uuid4())
        f = s.IG(f"a.b.{key}")
        with self.assertRaises(KeyError) as cm:
            f({'a': {'b': {}}})
        self.assertEqual(str(cm.exception), f"'{key}'")

    def test_multi_index(self):
        f = s.IG(1, 2, 4)
        v = self.create_sentinels('a0 a1 a2 a3 a4 a5')
        self.assertTupleEqual(f(v), (v.a1, v.a2, v.a4))

    def test_multi_key(self):
        f = s.IG('b', 'a')
        v = self.create_sentinels('a b')
        self.assertTupleEqual(f({'a': v.a, 'b': v.b}), (v.b, v.a))

    def test_deep_key(self):
        f = s.IG('meta.info.value')
        value = self.sentinel['value']
        self.assertIs(f({'meta': {'info': {'value': value}}}), value)

    def test_key_compose(self):
        with self.subTest('multi'):
            self.assertIsInstance(s.IG('a', 'b', 'c'), s.IG)

        with self.subTest('single'):
            self.assertIsInstance(s.IG('a'), s.IG)

        with self.subTest('deep'):
            r = s.IG('a.b.c')
            self.assertIsInstance(r, s.Compose)
            self.assertEqual(len(r.stack), 3)


if __name__ == "__main__":
    unittest.main()

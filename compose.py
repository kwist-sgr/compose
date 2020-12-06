from typing import Tuple, Callable
from reprlib import recursive_repr
from functools import partial, wraps, reduce
from operator import itemgetter, attrgetter, lshift


__version__ = '0.1.7'


def flip(func):

    @wraps(func)
    def wrapper(a, b):
        return func(b, a)

    return wrapper


def apply(func, arg):
    return func(arg)


def _name(obj):
    return obj.__class__.__name__


class Shift:

    def __lshift__(self, other):
        """ << operator """
        if isinstance(other, Shift):
            return Compose.pipeline(self, other)
        return NotImplemented


class Compose(Shift):
    """
    Container for function compositions
    """
    __slots__ = ('stack',)

    def __init__(self, *items):
        for x in items:
            if not isinstance(x, C):
                raise ValueError(f"Object must be 'C' instance, not {_name(x)!r}")
        self.stack = tuple(items)

    @classmethod
    def pipeline(cls, f, g):
        g_compose = isinstance(g, cls)
        if isinstance(f, cls):
            return cls(*f.stack, *g.stack) if g_compose else cls(*f.stack, g)
        return cls(f, *g.stack) if g_compose else cls(f, g)

    @recursive_repr()
    def __repr__(self):
        return f"<{_name(self)}: {','.join(map(repr, self.stack))}>"

    def __call__(self, arg):
        return reduce(flip(apply), reversed(self.stack), arg)


class C(Shift):
    """
    Function wrapper for compositions
    """
    __slots__ = ('func',)

    def __init__(self, func):
        self.func = func

    @property
    def __name__(self):
        return self.func.__name__

    def __repr__(self):
        return self.__name__

    def __call__(self, arg):
        return self.func(arg)


class BaseGetter(C):
    """
    Base class for getters
    """
    __slots__ = ('func', 'args',)

    def __init__(self, *args):
        super().__init__(self.getter(*args))
        self.args = args

    @property
    def __name__(self):
        return f"{_name(self)}({','.join(map(str, self.args))})"


class AG(BaseGetter):
    """
    Attribute getter
    """
    getter = attrgetter


class IG(BaseGetter):
    """
    Item getter
    """
    getter = itemgetter

    def __new__(cls, *args):
        try:
            arg, *others = args
        except ValueError:
            raise TypeError(f'{cls.getter.__name__} expected 1 argument, got 0')

        if isinstance(arg, str) and not others:
            # support dot-format, e.g. itemgetter('item.menu.id')
            names = arg.split('.')
            if len(names) > 1:
                return Compose(*map(cls, reversed(names)))

        # itemgetter(0), itemgetter(1, 2), itemgetter('item', 'date')
        return super().__new__(cls)


class P(C):
    """
    Partial function
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__(partial(func, *args, **kwargs))

    @property
    def __name__(self):
        return f"partial({self.func.func.__name__})"


class IterCompose(P):
    """
    Base class for iterators
    """
    f = None

    def __init__(self, func):
        super().__init__(self.f, func)

    @property
    def __name__(self):
        return f"{self.f.__name__}({self.func.args[0].__name__})"


class Map(IterCompose):
    f = map


class Filter(IterCompose):
    f = filter


Int = C(int)
Str = C(str)
Set = C(set)
List = C(list)
Dict = C(dict)

Sum = C(sum)

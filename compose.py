from typing import Tuple, Callable
from functools import partial, wraps, reduce
from operator import itemgetter, attrgetter, lshift


__version__ = '0.1.5'


def flip(func):

    @wraps(func)
    def wrapper(a, b):
        return func(b, a)

    return wrapper


def apply(func, arg):
    return func(arg)


class Shift:

    def __lshift__(self, other):
        """ << operator """
        if isinstance(other, Shift):
            return Compose.create(self, other)
        return NotImplemented


class Compose(Shift):
    """
    Container for function compositions
    """

    def __init__(self, *items):
        for x in items:
            if not isinstance(x, C):
                raise ValueError(f"Object must be 'C' instance, not {x.__class__.__name__!r}")
        self.stack = tuple(items)

    @classmethod
    def create(cls, f, g):
        if isinstance(f, cls):
            if isinstance(g, cls):
                return cls(*f.stack, *g.stack)
            return cls(*f.stack, g)
        if isinstance(g, cls):
            return cls(f, *g.stack)
        return cls(f, g)

    def __repr__(self):
        return f"<{self.__class__.__name__} [{','.join(map(repr, self.stack))}]>"

    def __call__(self, arg):
        return reduce(flip(apply), reversed(self.stack), arg)


class C(Shift):
    """
    Function wrapper for compositions
    """
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
    def __init__(self, *args):
        super().__init__(self.getter(*args))
        self.args = args

    @property
    def __name__(self):
        return f"{self.__class__.__name__}({','.join(map(str, self.args))})"


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
            raise TypeError('itemgetter expected 1 argument, got 0')

        if isinstance(arg, str) and not others:
            # support dot-format, e.g. itemgetter('item.menu.id')
            names = arg.split('.')
            if len(names) > 1:
                return reduce(lshift, map(cls, reversed(names)))

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

from functools import partial, wraps, reduce
from operator import itemgetter, attrgetter, lshift


def flip(func):

    @wraps(func)
    def wrapper(a, b):
        return func(b, a)

    return wrapper


def apply(func, arg):
    return func(arg)


class Compose:
    """
    Container for function compositions
    """
    __slots__ = ['stack']

    def __init__(self, f, g):
        f = f.stack if isinstance(f, self.__class__) else [f]
        g = g.stack if isinstance(g, self.__class__) else [g]
        self.stack = f + g

    def __repr__(self):
        return "<{} [{}]>".format(
            self.__class__.__name__,
            ','.join(map(attrgetter('__name__'), self.stack))
        )

    def __dir__(self):
        return ['__call__', '__class__']

    def __lshift__(self, other):
        """ << operator """
        return self.__class__(self, other)

    def __call__(self, arg, f=flip(apply)):
        return reduce(f, reversed(self.stack), arg)


class C:
    """
    Function wrapper for compositions
    """
    __slots__ = ['func']

    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return self.__name__

    def __dir__(self):
        return ['__call__', '__name__', '__class__']

    @property
    def __name__(self):
        return self.func.__name__

    def __lshift__(self, other):
        """ << operator """
        return Compose(self, other)

    def __call__(self, arg):
        return self.func(arg)


class BaseGetter(C):
    """
    Base class for getters
    """
    __slots__ = ['func', 'args']
    getter = None

    def __init__(self, *args):
        super(BaseGetter, self).__init__(self.getter(*args))
        self.args = ','.join(map(str, args))

    @property
    def __name__(self):
        return "{}({})".format(self.func.__class__.__name__, self.args)


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
        # support dot-format, e.g. itemgetter('item.menu.id')
        if len(args) == 1 and isinstance(args[0], str):
            names = args[0].split('.')
            if len(names) > 1:
                return reduce(lshift, map(cls, reversed(names)))
        # itemgetter(0), itemgetter(1, 2), itemgetter('item', 'date')
        return super(IG, cls).__new__(cls, *args)


class P(C):
    """
    Partial function
    """
    NAME_ID = 'partial'

    def __init__(self, func, *args, **kwargs):
        super(P, self).__init__(partial(func, *args, **kwargs))

    @property
    def __name__(self):
        return "{}({})".format(self.NAME_ID, self.func_name)

    @property
    def func_name(self):
        return self.func.func.__name__


class IterCompose(P):
    """
    Base class for iterators
    """
    f = None

    def __init__(self, func):
        super(IterCompose, self).__init__(self.f, func)

    @property
    def NAME_ID(self):
        return self.f.__name__

    @property
    def func_name(self):
        return self.func.args[0].__name__


class Map(IterCompose):
    f = map


class Filter(IterCompose):
    f = filter


Int = C(int)
Str = C(str)
Set = C(set)
List = C(list)

Sum = C(sum)

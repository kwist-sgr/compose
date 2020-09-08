from functools import partial, wraps, reduce
from operator import itemgetter, attrgetter, lshift


__version__ = '0.1.4'


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
        return Compose(self, other)


class Compose(Shift):
    """
    Container for function compositions
    """
    __slots__ = ['stack']

    def __init__(self, f, g):
        self.stack = []
        for x in (f, g):
            if isinstance(x, self.__class__):
                self.stack.extend(x.stack)
            else:
                self.stack.append(x)

    def __repr__(self):
        return "<{} [{}]>".format(
            self.__class__.__name__,
            ','.join(map(attrgetter('__name__'), self.stack))
        )

    def __call__(self, arg):
        return reduce(flip(apply), reversed(self.stack), arg)


class C(Shift):
    """
    Function wrapper for compositions
    """
    __slots__ = ['func']

    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return self.__name__

    @property
    def __name__(self):
        return self.func.__name__

    def __call__(self, arg):
        return self.func(arg)


class BaseGetter(C):
    """
    Base class for getters
    """
    __slots__ = ['func', 'args']
    getter = None
    NAME = None

    def __init__(self, *args):
        super().__init__(self.getter(*args))
        self.args = ','.join(map(str, args))

    @property
    def __name__(self):
        return f"{self.NAME}({self.args})"


class AG(BaseGetter):
    """
    Attribute getter
    """
    getter = attrgetter
    NAME = 'AG'


class IG(BaseGetter):
    """
    Item getter
    """
    getter = itemgetter
    NAME = 'IG'

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
    NAME = 'partial'

    def __init__(self, func, *args, **kwargs):
        super().__init__(partial(func, *args, **kwargs))

    @property
    def __name__(self):
        return f"{self.NAME}({self.func_name})"

    @property
    def func_name(self):
        return self.func.func.__name__


class IterCompose(P):
    """
    Base class for iterators
    """
    f = None

    def __init__(self, func):
        super().__init__(self.f, func)
        self.NAME = self.f.__name__

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
Dict = C(dict)

Sum = C(sum)

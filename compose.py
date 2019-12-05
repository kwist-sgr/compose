# coding: utf-8
from functools import partial, wraps
from itertools import imap, ifilter
from operator import itemgetter, attrgetter, or_


def flip(func):

    @wraps(func)
    def wrapper(a, b):
        return func(b, a)

    return wrapper


def apply(func, arg):
    return func(arg)


class Compose(object):
    __slots__ = ['stack']

    def __init__(self, f, g):
        f = f.stack if isinstance(f, self.__class__) else [f]
        g = g.stack if isinstance(g, self.__class__) else [g]
        self.stack = f + g

    def __repr__(self):
        return "<{} [{}]>".format(
            self.__class__.__name__,
            ','.join(imap(attrgetter('__name__'), self.stack))
        )

    def __dir__(self):
        return ['__call__', '__class__']

    def __or__(self, other):
        """ | operator """
        return self.__class__(self, other)

    def __ior__(self, other):
        """ |= operator """
        if isinstance(other, self.__class__):
            self.stack.extend(other.stack)
        else:
            self.stack.append(other)
        return self

    def __call__(self, arg, f=flip(apply)):
        return reduce(f, reversed(self.stack), arg)


class C(object):
    __slots__ = ['func', '__doc__']

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __repr__(self):
        return self.__name__

    def __dir__(self):
        return ['__call__', '__name__', '__doc__', '__class__']

    @property
    def __name__(self):
        return self.func.__name__

    def __or__(self, other):
        """ | operator """
        return Compose(self, other)

    def __call__(self, arg):
        return self.func(arg)


class BaseGetter(C):
    __slots__ = ['func', '__doc__', 'args']
    getter = None

    def __init__(self, *args):
        super(BaseGetter, self).__init__(self.getter(*args))
        self.args = ','.join(imap(str, args))

    @property
    def __name__(self):
        return "{}({})".format(self.func.__class__.__name__, self.args)


class AG(BaseGetter):
    getter = attrgetter


class IG(BaseGetter):
    getter = itemgetter

    def __new__(cls, *args):
        # support dot-format, e.g. itemgetter('item.menu.id')
        if len(args) == 1 and isinstance(args[0], basestring):
            names = args[0].split('.')
            if len(names) > 1:
                return reduce(or_, imap(cls, reversed(names)))
        # itemgetter(0), itemgetter(1, 2), itemgetter('item', 'date')
        return super(IG, cls).__new__(cls, *args)


class P(C):
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
    f = imap


class Filter(IterCompose):
    f = ifilter


Int = C(int)
Str = C(str)
Set = C(set)
List = C(list)

Sum = C(sum)

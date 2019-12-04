# coding: utf-8
from functools import partial
from itertools import imap, ifilter
from operator import itemgetter, attrgetter, rshift


class Compose(object):

    def __init__(self, f, g):
        self.stack = [f, g]

    def __repr__(self):
        return "<{} [{}]>".format(
            self.__class__.__name__,
            ','.join(imap(attrgetter('__name__'), self.stack))
        )

    def __rshift__(self, other):
        if isinstance(other, self.__class__):
            self.stack.extend(other.stack)
        else:
            self.stack.append(other)
        return self

    def __call__(self, arg):
        return reduce(lambda arg, f: f(arg), self.stack, arg)


class C(object):

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __repr__(self):
        return self.__name__

    @property
    def __name__(self):
        return self.func.__name__

    def __rshift__(self, other):
        """ >> operator """
        return Compose(self, other)

    def __call__(self, arg):
        return self.func(arg)


class BaseGetter(C):
    getter = None

    def __init__(self, *args):
        self.args = args
        super(BaseGetter, self).__init__(self.getter(*args))

    @property
    def __name__(self):
        return "{}({})".format(self.func.__class__.__name__, ','.join(imap(str, self.args)))


class AG(BaseGetter):
    getter = attrgetter


class IG(BaseGetter):
    getter = itemgetter

    def __new__(cls, *args):
        # support dot-format, e.g. itemgetter('item.menu.id')
        if len(args) == 1 and isinstance(args[0], basestring):
            names = args[0].split('.')
            if len(names) > 1:
                return reduce(rshift, imap(cls, names))
        # itemgetter(0), itemgetter(1, 2), itemgetter('item', 'date')
        return super(IG, cls).__new__(cls, *args)


class P(C):
    NAME_ID = 'partial'

    def __init__(self, func, *args, **kwargs):
        super(P, self).__init__(partial(func, *args, **kwargs))
        self.func_name = func.__name__

    @property
    def __name__(self):
        return "{}({})".format(self.NAME_ID, self.func_name)


class ItertoolsPartial(P):
    f = None

    @property
    def NAME_ID(self):
        return self.f.__name__

    def __init__(self, func):
        super(ItertoolsPartial, self).__init__(self.f, func)
        self.func_name = func.__name__


class Map(ItertoolsPartial):
    f = imap


class Filter(ItertoolsPartial):
    f = ifilter


Int = C(int)
Str = C(str)
Set = C(set)
List = C(list)

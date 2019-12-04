# coding: utf-8
from itertools import imap
from functools import partial
from operator import itemgetter, attrgetter, rshift


__all__ = ['C', 'Int', 'Str', 'IG', 'AG', 'P']


def apply(arg, f):
    return f(arg)


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
        return reduce(apply, self.stack, arg)


class C(object):

    def __init__(self, func):
        self.func = func

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

    def __init__(self, func, *args, **kwargs):
        super(P, self).__init__(partial(func, *args, **kwargs))

    @property
    def __name__(self):
        return "partial({})".format(self.func.func.__name__)


Int = C(int)
Str = C(str)


"""

# f = lambda x: int(x['id'])
In : f = IG('id') >> Int
In : f({'id': '75', 'test': True})
Out: 75

# f = lambda x: list(str(int(x['id'])))
In : f = IG('id') >> Int >> Str >> C(list)
In : f({'id': '75', 'test': True})
Out: ['7', '5']

# f = lambda x: max(7, int(x['id]))
In : f = IG('id') >> Int >> P(max, 7)
In : f({'id': '75', 'test': True})
Out: 75
In : f({'id': '5', 'test': True})
Out: 7

# f = lambda x: list(str(max, 777, int(x['id'])))
In : f = IG('id') >> Int >> P(max, 777) >> Str >> C(list)
In : f
Out: <Compose [itemgetter('id'),int,partial('max'),str,list]>

In : f({'id': '75', 'test': True})
Out: ['7', '7', '7']

In : f({'id': '1275', 'test': True})
Out: ['1', '2', '7', '5']

# f = lambda x: int(x['item']['id'])
In : f = IG('item.id') >> Int
In : f
Out: <Compose [itemgetter('item'),itemgetter('id'),int]>
In : f({'item': {'id': '742', 'flag': 7}})
Out: 742

# f = lambda x: list(str(max(721, int(x['item']['id']))))
In : f = IG('item.id') >> Int >> P(max, 721) >> Str >> C(list)
In : f
Out: <Compose [itemgetter('item'),itemgetter('id'),int,partial('max'),str,list]>

In : f({'item': {'id': '742', 'flag': 7}})
Out: ['7', '4', '2']

# f = lambda x: list(str(int(x['item']['id'][1])))
In : f = IG('item.id') >> IG(1) >> Int >> Str >> C(list)
In : f
Out: <Compose [itemgetter(item),itemgetter(id),itemgetter(1),int,str,list]>

In : f({'item': {'id': ['742', '15', '98'], 'flag': 7}})
Out: ['1', '5']

"""

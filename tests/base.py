from collections import namedtuple


class _SentinelObject:
    "A unique, named, sentinel object."
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'sentinel.{self.name}'

    def __reduce__(self):
        return f'sentinel.{self.name}'


class _Sentinel:
    """Access items to return a named object, usable as a sentinel."""

    def __getitem__(self, name):
        return _SentinelObject(name)

    def __reduce__(self):
        return 'sentinel'

    def batch(self, names):
        Row = namedtuple('Row', names)
        return Row._make(self.sentinel[f'value_{f}'] for f in Row._fields)


sentinel = _Sentinel()

import compose as cp


def test_int():
    assert isinstance(cp.Int, cp.C)
    assert cp.Int.func is int
    assert cp.Int('25') == 25


def test_str():
    assert isinstance(cp.Str, cp.C)
    assert cp.Str.func is str
    assert cp.Str(26) == '26'


def test_set():
    assert isinstance(cp.Set, cp.C)
    assert cp.Set.func is set
    assert cp.Set('251125') == {'1', '2', '5'}


def test_list():
    assert isinstance(cp.List, cp.C)
    assert cp.List.func is list
    assert cp.List('25125') == ['2', '5', '1', '2', '5']


def test_dict():
    assert isinstance(cp.Dict, cp.C)
    assert cp.Dict.func is dict
    assert cp.Dict([('x', 15), ('y', 'Y'), ('z', [1])]) == {'x': 15, 'y': 'Y', 'z': [1]}


def test_sum():
    assert isinstance(cp.Sum, cp.C)
    assert cp.Sum.func is sum
    assert cp.Sum([1, 5, 9, 2]) == 17

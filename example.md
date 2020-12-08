```python
# f = lambda x: int(x['id'])
In : f = Int << IG('id')
In : f({'id': '75', 'test': True})
Out: 75
```

```python
# f = lambda x: list(str(int(x['id'])))
In : f = List << Str << Int << IG('id')
In : f({'id': '75', 'test': True})
Out: ['7', '5']
```

```python
# f = lambda x: max(7, int(x['id]))
In : f = P(max, 7) << Int << IG('id')
In : f({'id': '75', 'test': True})
Out: 75
In : f({'id': '5', 'test': True})
Out: 7
```

```python
# f = lambda x: list(str(max, 777, int(x['id'])))
In : f = List << Str << P(max, 777) << Int << IG('id')
In : f
Out: <Compose list,str,partial(max),int,itemgetter(id)>

In : f({'id': '75', 'test': True})
Out: ['7', '7', '7']

In : f({'id': '1275', 'test': True})
Out: ['1', '2', '7', '5']
```

```python
# f = lambda x: int(x['item']['id'])
In : f = Int << IG('item.id')
In : f
Out: <Compose int,itemgetter(id),itemgetter(item)>

In : f({'item': {'id': '742', 'flag': 7}})
Out: 742
```

```python
# f = lambda x: list(str(max(721, int(x['item']['id']))))
In : f = List << Str << P(max, 721) << Int << IG('item.id')
In : f
Out: <Compose list,str,partial(max),int,itemgetter(id),itemgetter(item)>

In : f({'item': {'id': '742', 'flag': 7}})
Out: ['7', '4', '2']
```

```python
# f = lambda x: list(str(int(x['item']['id'][1])))
In : f = List << Str << Int << IG(1) << IG('item.id')
In : f
Out: <Compose list,str,int,itemgetter(1),itemgetter(id),itemgetter(item)>

In : f({'item': {'id': ['742', '15', '98'], 'flag': 7}})
Out: ['1', '5']
```

```python
# f = lambda x: list(map(int, x))
In : f = List << Map(int)
In : f
Out: <Compose list,map(int)>

In : f(['4', '7'])
Out: [4, 7]

In : f = Sum << Map(int)
In : f
Out: <Compose sum,map(int)>

In : f('471')
Out: 12
```

```python
# f = lambda m: {x[0] for x in m}
In : f = Set << Map(IG(0))
In : f
Out: <Compose set,map(itemgetter(0))>

In : f([(1, '1'), (50, '05'), (11, '21'), (50, '50')])
Out: set([1, 50, 11])
```

```python
# f = lambda x: sum(map(int, list(str(max(721, int(x['item']['id']))))))
In : f = Sum << Map(int) << List << Str << P(max, 721) << Int << IG('item.id')
In : f
Out: <Compose sum,map(int),list,str,partial(max),int,itemgetter(id),itemgetter(item)>

In : f({'item': {'id': '742', 'flag': 7}})
Out: 13
```

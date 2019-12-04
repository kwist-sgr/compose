```python
# f = lambda x: int(x['id'])
In : f = IG('id') >> Int
In : f({'id': '75', 'test': True})
Out: 75
```

```python
# f = lambda x: list(str(int(x['id'])))
In : f = IG('id') >> Int >> Str >> C(list)
In : f({'id': '75', 'test': True})
Out: ['7', '5']
```

```python
# f = lambda x: max(7, int(x['id]))
In : f = IG('id') >> Int >> P(max, 7)
In : f({'id': '75', 'test': True})
Out: 75
In : f({'id': '5', 'test': True})
Out: 7
```

```python
# f = lambda x: list(str(max, 777, int(x['id'])))
In : f = IG('id') >> Int >> P(max, 777) >> Str >> C(list)
In : f
Out: <Compose [itemgetter('id'),int,partial('max'),str,list]>

In : f({'id': '75', 'test': True})
Out: ['7', '7', '7']

In : f({'id': '1275', 'test': True})
Out: ['1', '2', '7', '5']
```

```python
# f = lambda x: int(x['item']['id'])
In : f = IG('item.id') >> Int
In : f
Out: <Compose [itemgetter('item'),itemgetter('id'),int]>
In : f({'item': {'id': '742', 'flag': 7}})
Out: 742
```

```python
# f = lambda x: list(str(max(721, int(x['item']['id']))))
In : f = IG('item.id') >> Int >> P(max, 721) >> Str >> C(list)
In : f
Out: <Compose [itemgetter('item'),itemgetter('id'),int,partial('max'),str,list]>

In : f({'item': {'id': '742', 'flag': 7}})
Out: ['7', '4', '2']
```

```python
# f = lambda x: list(str(int(x['item']['id'][1])))
In : f = IG('item.id') >> IG(1) >> Int >> Str >> C(list)
In : f
Out: <Compose [itemgetter(item),itemgetter(id),itemgetter(1),int,str,list]>

In : f({'item': {'id': ['742', '15', '98'], 'flag': 7}})
Out: ['1', '5']
```

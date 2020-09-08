===============================
Function Composition in Python.
===============================

.. teaser-begin

Compose is a package for `function composition <https://en.wikipedia.org/wiki/Function_composition_(computer_science)>`_ in python.

.. teaser-end

Restrictions
------------

Only functions with one argument are supported.

Installation
------------

.. code-block:: console

    >>> pip install compose
  
Examples
--------

.. -code-begin-

.. code:: pycon

    >>> from compose import Int, IG, Sum, Map, Dict
   
    >>> f = Int << IG('item.id')   # f = lambda x: int(x['item']['id'])
    >>> f({'item': {'id': '75', 'v': 1}})
    75

    >>> f = Sum << Map(int)  # f = lambda x: sum(map(int, x))
    >>> f('471')
    12

    >>> f = Sum << Map(int) << IG(1) << IG('item.x')  # f = lambda x: sum(map(int, x['item']['id'][1]))
    >>> f({'item': {'x': ['742', '153', '98'], 'f': 7}})
    9
    
    >>> f = Dict << Map(IG(0, 2))  # f = lambda x: dict(map(itemgetter(0, 2), x))
    >>> f([('a', 17, 71), ('b', 26, 62), ('c', 39, 93)])
    {'a': 71, 'b': 62, 'c': 93}

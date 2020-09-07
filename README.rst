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

    >>> from compose import Int, IG, Sum, Map
   
    >>> f = Int << IG('item.id')   # f = lambda x: int(x['item']['id'])
    >>> f
    <Compose [int,itemgetter(id),itemgetter(item)]>
    >>> f({'item': {'id': '75', 'v': 1}})
    75

    >>> f = Sum << Map(int)  # f = lambda x: sum(map(int, x))
    >>> f('471')
    12

    >>> f = Sum << Map(int) << IG(1) << IG('item.x')  # f = lambda x: sum(map(int, x['item']['id'][1]))
    >>> f
    <Compose [sum,map(int),itemgetter(1),itemgetter(x),itemgetter(item)]>
    >>> f({'item': {'x': ['742', '153', '98'], 'f': 7}})
    9

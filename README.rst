===============================
Function Composition in Python.
===============================

.. teaser-begin

Compose is a package for `function composition <https://en.wikipedia.org/wiki/Function_composition_(computer_science)>`_ in python.

.. teaser-end

Installation
------------

.. code-block:: console

    >>> pip install compose
  
Compose example
---------------

.. -code-begin-

.. code:: pycon

    >>> from compose import Int, IG
   
    >>> f = Int << IG('id')  # analog of lambda x: int(x['id'])

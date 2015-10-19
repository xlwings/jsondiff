jsondiff
========

.. code-block:: python

    >>> from jsondiff import diff
    
    >>> diff({'a': 1}, {'a': 1, 'b': 2})
    {<insert>: {'b': 2}}
    
    >>> diff({'a': 1, 'b': 3}, {'a': 1, 'b': 2})
    {<update>: {'b': 2}}
    
    >>> diff({'a': 1, 'b': 3}, {'a': 1})
    {<delete>: ['b']}
    
    >>> diff(['a', 'b', 'c'], ['a', 'b', 'c', 'd'])
    {<insert>: [(3, 'd')]}
    
    >>> diff(['a', 'b', 'c'], ['a', 'c'])
    {<delete>: [1]}
    
    # Similar items get patched
    >>> diff(['a', {'x': 3}, 'c'], ['a', {'x': 3, 'y': 4}, 'c'])
    {<update>: [(1, {<insert>: {'y': 4}})]}
    
    # Special handling of sets
    >>> diff({'a', 'b', 'c'}, {'a', 'c', 'd'})
    {<add>: set(['d']), <discard>: set(['b'])}
    
    # Parse and dump JSON
    >>> print diff('["a", "b", "c"]', '["a", "c", "d"]', parse=True, dump=True, indent=2)
    {
      "$delete": [
        1
      ],
      "$insert": [
        [
          2,
          "d"
        ]
      ]
    }
    

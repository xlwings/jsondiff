jsondiff
========

.. code-block:: python

    >>> from jsondiff import diff

    >>> diff({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
    {<delete>: ['a'], 'c': 4, 'b': 3}

    >>> diff(['a', 'b', 'c'], ['a', 'b', 'c', 'd'])
    {<insert>: [(3, 'd')]}

    >>> diff(['a', 'b', 'c'], ['a', 'c'])
    {<delete>: [1]}

    # Typical diff looks like what you'd expect...
    >>> diff({'a': [0, {'b': 4}, 1]}, {'a': [0, {'b': 5}, 1]})
    {'a': {1: {'b': 5}}}

    # ...but similarity is taken into account
    >>> diff({'a': [0, {'b': 4}, 1]}, {'a': [0, {'c': 5}, 1]})
    {'a': {<delete>: [1], <insert>: [(1, {'c': 5})]}}

    # Special handling of sets
    >>> diff({'a', 'b', 'c'}, {'a', 'c', 'd'})
    {<discard>: set(['b']), <add>: set(['d'])}

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

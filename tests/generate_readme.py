def do(cmd, comment=None):
    if comment:
        print "# " + comment
    print ">>> " + cmd
    c = compile(cmd, filename="<string>", mode='single')
    eval(c, globals())
    print

do('from jsondiff import diff')

do("diff({'a': 1}, {'a': 1, 'b': 2})")

do("diff({'a': 1, 'b': 3}, {'a': 1, 'b': 2})")

do("diff({'a': 1, 'b': 3}, {'a': 1})")

do("diff(['a', 'b', 'c'], ['a', 'b', 'c', 'd'])")

do("diff(['a', 'b', 'c'], ['a', 'c'])")

do("diff(['a', {'x': 3}, 'c'], ['a', {'x': 3, 'y': 4}, 'c'])", "Similar items get patched")

do("diff({'a', 'b', 'c'}, {'a', 'c', 'd'})", "Special handling of sets")

do("print diff('[\"a\", \"b\", \"c\"]', '[\"a\", \"c\", \"d\"]', parse=True, dump=True, indent=2)", "Parse and dump JSON")
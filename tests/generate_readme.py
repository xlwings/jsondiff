# this file doesn't work in Py3 - but it's only used for generating the repo front page

def do(cmd, comment=None):
    if comment:
        print "# " + comment
    print ">>> " + cmd
    c = compile(cmd, filename="<string>", mode='single')
    eval(c, globals())
    print

do('from jsondiff import diff')

do("diff({'a': 1, 'b': 2}, {'b': 3, 'c': 4})")

do("diff(['a', 'b', 'c'], ['a', 'b', 'c', 'd'])")

do("diff(['a', 'b', 'c'], ['a', 'c'])")

do("diff({'a': [0, {'b': 4}, 1]}, {'a': [0, {'b': 5}, 1]})", "Typical diff looks like what you'd expect...")

do("diff({'a': [0, {'b': 4}, 1]}, {'a': [0, {'c': 5}, 1]})", "...but similarity is taken into account")

do("diff({'a': 1, 'b': 2}, {'b': 3, 'c': 4}, syntax='explicit')", "Support for various diff syntaxes")

do("diff({'a': 1, 'b': 2}, {'b': 3, 'c': 4}, syntax='symmetric')")

do("diff({'a', 'b', 'c'}, {'a', 'c', 'd'})", "Special handling of sets")

do("print diff('[\"a\", \"b\", \"c\"]', '[\"a\", \"c\", \"d\"]', load=True, dump=True)", "Load and dump JSON")


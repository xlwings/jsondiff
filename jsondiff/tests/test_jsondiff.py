import sys
import unittest

from random import Random

from .. import diff, replace, add, discard, insert, delete, update, JsonDiffer
from .utils import generate_random_json, perturbate_json

import pytest

class JsonDiffTests(unittest.TestCase):

    def _generate_tag(n, rng):
        return ''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(n))

    def randomize(self, n, generator, seed=12038728732):
        def decorator(func):
            def randomized_test(self):
                rng_seed = Random(seed)
                nseeds = n
                seeds = (rng_seed.getrandbits(32) for i in range(n))
                for i, rseed in enumerate(seeds):
                    rng = Random(rseed)
                    scenario = generator(self, rng)
                    try:
                        func(self, scenario)
                    except Exception as e:
                        import sys
                        raise type(e).with_traceback(type(e)('%s with scenario %s (%i of %i)' % (e.message, rseed, i+1, nseeds)), sys.exc_info()[2])
                return(randomized_test)
        return decorator

    def test_a(self):
        assert {} == diff(1, 1)
        assert {} == diff(True, True)
        assert {} == diff('abc', 'abc')
        assert {} == diff([1, 2], [1, 2])
        assert {} == diff((1, 2), (1, 2))
        assert {} == diff({1, 2}, {1, 2})
        assert {} == diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2})
        assert {} == diff([], [])
        assert {} == diff(None, None)
        assert {} == diff({}, {})
        assert {} == diff(set(), set())

        assert 2 == diff(1, 2)
        assert False == diff(True, False)
        assert 'def' == diff('abc', 'def')
        assert [3, 4] == diff([1, 2], [3, 4])
        assert (3, 4) == diff((1, 2), (3, 4))
        assert {3, 4} == diff({1, 2}, {3, 4})
        assert {replace: {'c': 3, 'd': 4}} == diff({'a': 1, 'b': 2}, {'c': 3, 'd': 4})

        assert {replace: {'c': 3, 'd': 4}} == diff([1, 2], {'c': 3, 'd': 4})
        assert 123 == diff({'a': 1, 'b': 2}, 123)

        assert {delete: ['b']} == diff({'a': 1, 'b': 2}, {'a': 1})
        assert {'b': 3} == diff({'a': 1, 'b': 2}, {'a': 1, 'b': 3})
        assert {'c': 3} == diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3})
        assert {delete: ['b'], 'c': 3} == diff({'a': 1, 'b': 2}, {'a': 1, 'c': 3})

        assert {add: {3}} == diff({1, 2}, {1, 2, 3})
        assert {add: {3}, discard: {4}} == diff({1, 2, 4}, {1, 2, 3})
        assert {discard: {4}} == diff({1, 2, 4}, {1, 2})

        assert {insert: [(1, 'b')]} == diff(['a', 'c'], ['a', 'b', 'c'])
        assert {insert: [(1, 'b')], delete: [3, 0]} == diff(['x', 'a', 'c', 'x'], ['a', 'b', 'c'])
        assert {insert: [(2, 'b')], delete: [4, 0], 1: {'v': 20}} == diff(['x', 'a', {'v': 11}, 'c', 'x'], ['a', {'v': 20}, 'b', 'c'])
        assert {insert: [(2, 'b')], delete: [4, 0],  1: {'v': 20}} == diff(['x', 'a', {'u': 10, 'v': 11}, 'c', 'x'], ['a', {'u': 10, 'v': 20}, 'b', 'c'])

    def test_marshal(self):
        differ = JsonDiffer()

        d = {
            delete: 3,
            '$delete': 4,
            insert: 4,
            '$$something': 1
        }

        dm = differ.marshal(d)

        assert d == differ.unmarshal(dm)

    def generate_scenario(self, rng):
        a = generate_random_json(rng, sets=True)
        b = perturbate_json(a, rng, sets=True)
        return a, b

    def generate_scenario_no_sets(self, rng):
        a = generate_random_json(rng, sets=False)
        b = perturbate_json(a, rng, sets=False)
        return a, b

    def test_dump(self):
        @self.randomize(self, 1000, self.generate_scenario_no_sets)
        def dump(self, scenario):
            a, b = scenario
            diff(a, b, syntax='compact', dump=True)
            diff(a, b, syntax='explicit', dump=True)
            diff(a, b, syntax='symmetric', dump=True)

    def test_compact_syntax(self):
        @self.randomize(self, 1000, self.generate_scenario)
        def compact_syntax(self, scenario):
            a, b = scenario
            differ = JsonDiffer(syntax='compact')
            d = differ.diff(a, b)
            assert b == differ.patch(a, d)
            dm = differ.marshal(d)
            assert d == differ.unmarshal(dm)

    def test_explicit_syntax(self):
        @self.randomize(self, 1000, self.generate_scenario)
        def explicit_syntax(self, scenario):
            a, b = scenario
            differ = JsonDiffer(syntax='explicit')
            d = differ.diff(a, b)
            # assert b == differ.patch(a, d)
            dm = differ.marshal(d)
            assert d == differ.unmarshal(dm)

    def test_symmetric_syntax(self):
        @self.randomize(self, 1000, self.generate_scenario)
        def symmetric_syntax(self, scenario):
            a, b = scenario
            differ = JsonDiffer(syntax='symmetric')
            d = differ.diff(a, b)
            assert b == differ.patch(a, d)
            assert a == differ.unpatch(b, d)
            dm = differ.marshal(d)
            assert d == differ.unmarshal(dm)

    def test_long_arrays(self):
        size = 100
        a = [{'a': i, 'b': 2 * i} for i in range(1, size)]
        b = [{'a': i, 'b': 3 * i} for i in range(1, size)]
        r = sys.getrecursionlimit()
        sys.setrecursionlimit(size - 1)

        try:
            diff(a, b)
        except RecursionError:
            pytest.fail('cannot diff long arrays')
        finally:
            sys.setrecursionlimit(r)

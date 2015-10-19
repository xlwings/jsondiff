import unittest

from jsondiff import diff, identical, add, discard, insert, delete, update


class JsonDiffTests(unittest.TestCase):

    def test_a(self):

        self.assertIs(identical, diff(1, 1))
        self.assertIs(identical, diff(True, True))
        self.assertIs(identical, diff('abc', 'abc'))
        self.assertIs(identical, diff([1, 2], [1, 2]))
        self.assertIs(identical, diff((1, 2), (1, 2)))
        self.assertIs(identical, diff({1, 2}, {1, 2}))
        self.assertIs(identical, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2}))

        self.assertEqual(2, diff(1, 2))
        self.assertEqual(False, diff(True, False))
        self.assertEqual('def', diff('abc', 'def'))
        self.assertEqual([3, 4], diff([1, 2], [3, 4]))
        self.assertEqual((3, 4), diff((1, 2), (3, 4)))
        self.assertEqual({3, 4}, diff({1, 2}, {3, 4}))
        self.assertEqual({'c': 3, 'd': 4}, diff({'a': 1, 'b': 2}, {'c': 3, 'd': 4}))

        self.assertEqual({'c': 3, 'd': 4}, diff([1, 2], {'c': 3, 'd': 4}))
        self.assertEqual(123, diff({'a': 1, 'b': 2}, 123))

        self.assertEqual({delete: ['b']}, diff({'a': 1, 'b': 2}, {'a': 1}))
        self.assertEqual({update: {'b': 3}}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 3}))
        self.assertEqual({insert: {'c': 3}}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3}))
        self.assertEqual({delete: ['b'], insert: {'c': 3}}, diff({'a': 1, 'b': 2}, {'a': 1, 'c': 3}))

        self.assertEqual({add: {3}}, diff({1, 2}, {1, 2, 3}))
        self.assertEqual({add: {3}, discard: {4}}, diff({1, 2, 4}, {1, 2, 3}))
        self.assertEqual({discard: {4}}, diff({1, 2, 4}, {1, 2}))

        self.assertEqual({insert: [(1, 'b')]}, diff(['a', 'c'], ['a', 'b', 'c']))
        self.assertEqual({insert: [(1, 'b')], delete: [0, 3]}, diff(['x', 'a', 'c', 'x'], ['a', 'b', 'c']))
        self.assertEqual(
            {insert: [(1, {'v': 20}), (2, 'b')], delete: [0, 2, 4]},
            diff(['x', 'a', {'v': 11}, 'c', 'x'], ['a', {'v': 20}, 'b', 'c'])
        )
        self.assertEqual(
            {insert: [(2, 'b')], delete: [0, 4], update: [(1, {update: {'v': 20}})]},
            diff(['x', 'a', {'u': 10, 'v': 11}, 'c', 'x'], ['a', {'u': 10, 'v': 20}, 'b', 'c'])
        )

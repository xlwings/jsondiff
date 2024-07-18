import io
import logging
import os.path
import sys
import unittest
import pytest

import jsondiff
from jsondiff import diff, replace, add, discard, insert, delete, JsonDiffer

from .utils import generate_random_json, perturbate_json

from hypothesis import given, settings, strategies


logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s %(pathname)s[line:%(lineno)d] %(levelname)s %(message)s'
    ),
)
logging.getLogger("jsondiff").setLevel(logging.DEBUG)


def generate_scenario(rng):
    a = generate_random_json(rng, sets=True)
    b = perturbate_json(a, rng, sets=True)
    return a, b


def generate_scenario_no_sets(rng):
    a = generate_random_json(rng, sets=False)
    b = perturbate_json(a, rng, sets=False)
    return a, b


class JsonDiffTests(unittest.TestCase):

    def test_a(self):

        self.assertEqual({}, diff(1, 1))
        self.assertEqual({}, diff(True, True))
        self.assertEqual({}, diff('abc', 'abc'))
        self.assertEqual({}, diff([1, 2], [1, 2]))
        self.assertEqual({}, diff((1, 2), (1, 2)))
        self.assertEqual({}, diff({1, 2}, {1, 2}))
        self.assertEqual({}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2}))
        self.assertEqual({}, diff([], []))
        self.assertEqual({}, diff(None, None))
        self.assertEqual({}, diff({}, {}))
        self.assertEqual({}, diff(set(), set()))

        self.assertEqual(2, diff(1, 2))
        self.assertEqual(False, diff(True, False))
        self.assertEqual('def', diff('abc', 'def'))
        self.assertEqual([3, 4], diff([1, 2], [3, 4]))
        self.assertEqual((3, 4), diff((1, 2), (3, 4)))
        self.assertEqual({3, 4}, diff({1, 2}, {3, 4}))
        self.assertEqual({replace: {'c': 3, 'd': 4}}, diff({'a': 1, 'b': 2}, {'c': 3, 'd': 4}))

        self.assertEqual({replace: {'c': 3, 'd': 4}}, diff([1, 2], {'c': 3, 'd': 4}))
        self.assertEqual(123, diff({'a': 1, 'b': 2}, 123))

        self.assertEqual({delete: ['b']}, diff({'a': 1, 'b': 2}, {'a': 1}))
        self.assertEqual({'b': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 3}))
        self.assertEqual({'c': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3}))
        self.assertEqual({delete: ['b'], 'c': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'c': 3}))

        self.assertEqual({add: {3}}, diff({1, 2}, {1, 2, 3}))
        self.assertEqual({add: {3}, discard: {4}}, diff({1, 2, 4}, {1, 2, 3}))
        self.assertEqual({discard: {4}}, diff({1, 2, 4}, {1, 2}))

        self.assertEqual({insert: [(1, 'b')]}, diff(['a', 'c'], ['a', 'b', 'c']))
        self.assertEqual({insert: [(1, 'b')], delete: [3, 0]}, diff(['x', 'a', 'c', 'x'], ['a', 'b', 'c']))
        self.assertEqual(
            {insert: [(2, 'b')], delete: [4, 0], 1: {'v': 20}},
            diff(['x', 'a', {'v': 11}, 'c', 'x'], ['a', {'v': 20}, 'b', 'c'])
        )
        self.assertEqual(
            {insert: [(2, 'b')], delete: [4, 0],  1: {'v': 20}},
            diff(['x', 'a', {'u': 10, 'v': 11}, 'c', 'x'], ['a', {'u': 10, 'v': 20}, 'b', 'c'])
        )

    def test_marshal(self):
        differ = JsonDiffer()

        d = {
            delete: 3,
            '$delete': 4,
            insert: 4,
            '$$something': 1
        }

        dm = differ.marshal(d)

        self.assertEqual(d, differ.unmarshal(dm))

    @given(strategies.randoms().map(generate_scenario_no_sets))
    @settings(max_examples=1000)
    def test_dump(self, scenario):
        a, b = scenario
        diff(a, b, syntax='compact', dump=True)
        diff(a, b, syntax='explicit', dump=True)
        diff(a, b, syntax='symmetric', dump=True)

    @given(strategies.randoms().map(generate_scenario))
    @settings(max_examples=1000)
    def test_compact_syntax(self, scenario):
        a, b = scenario
        differ = JsonDiffer(syntax='compact')
        d = differ.diff(a, b)
        self.assertEqual(b, differ.patch(a, d))
        dm = differ.marshal(d)
        self.assertEqual(d, differ.unmarshal(dm))


    @given(strategies.randoms().map(generate_scenario))
    @settings(max_examples=1000)
    def test_explicit_syntax(self, scenario):
        a, b = scenario
        differ = JsonDiffer(syntax='explicit')
        d = differ.diff(a, b)
        # self.assertEqual(b, differ.patch(a, d))
        dm = differ.marshal(d)
        self.assertEqual(d, differ.unmarshal(dm))

    @given(strategies.randoms().map(generate_scenario))
    @settings(max_examples=1000)
    def test_symmetric_syntax(self, scenario):
        a, b = scenario
        differ = JsonDiffer(syntax='symmetric')
        d = differ.diff(a, b)
        self.assertEqual(b, differ.patch(a, d))
        self.assertEqual(a, differ.unpatch(b, d))
        dm = differ.marshal(d)
        self.assertEqual(d, differ.unmarshal(dm))

    def test_long_arrays(self):
        size = 100
        a = [{'a': i, 'b': 2 * i} for i in range(1, size)]
        b = [{'a': i, 'b': 3 * i} for i in range(1, size)]
        r = sys.getrecursionlimit()
        sys.setrecursionlimit(size - 1)

        try:
            diff(a, b)
        except RecursionError:
            self.fail('cannot diff long arrays')
        finally:
            sys.setrecursionlimit(r)


@pytest.mark.parametrize(
    ("a", "b", "syntax", "expected"),
    [
        pytest.param([], [{"a": True}], "explicit", {insert: [(0, {"a": True})]},
                     id="issue59_"),
        pytest.param([{"a": True}], [], "explicit", {delete: [0]},
                     id="issue59_"),
        pytest.param([], [{"a": True}], "compact", [{"a": True}],
                     id="issue59_"),
        pytest.param([{"a": True}], [], "compact", [],
                     id="issue59_"),
        pytest.param([], [{"a": True}], "symmetric", {insert: [(0, {"a": True})]},
                     id="issue59_"),
        pytest.param([{"a": True}], [], "symmetric", {delete: [(0, {"a": True})]},
                     id="issue59_"),
        pytest.param({1: 2}, {5: 3}, "symmetric", {delete: {1: 2}, insert: {5: 3}},
                     id="issue36_"),
        pytest.param({1: 2}, {5: 3}, "compact", {replace: {5: 3}},
                     id="issue36_"),
    ],
)
class TestSpecificIssue:
    def test_issue(self,  a, b, syntax, expected):
        actual = diff(a, b, syntax=syntax)
        assert actual == expected


class TestRightOnly(unittest.TestCase):
    def test_right_only_syntax(self):
        a = {"poplist": [1, 2, 3]}
        b = {}
        self.assertEqual(
            diff(a, b, syntax="rightonly", marshal=True),
            {
                "$delete": ["poplist"],
            }
        )
        a = {1: 2, 2: 3, 'list': [1, 2, 3], 'samelist': [1, 2, 3], "poplist": [1, 2, 3]}
        b = {1: 2, 2: 4, 'list': [1, 3], 'samelist': [1, 2, 3]}
        self.assertEqual(
            diff(a, b, syntax="rightonly", marshal=True),
            {
                2: 4,
                "list": [1, 3],
                "$delete": ["poplist"],
            }
        )
        self.assertEqual(
            diff(a, b, syntax="rightonly"),
            {
                2: 4,
                "list": [1, 3],
                delete: ["poplist"],
            }
        )
        c = [1, 2, 3]
        d = [4, 5, 6]
        self.assertEqual(
            diff(c, d, syntax="rightonly", marshal=True),
            [4, 5, 6],
        )

class TestLoaders(unittest.TestCase):

    here = os.path.dirname(__file__)
    data_dir = os.path.join(here, "data")

    def test_json_string_loader(self):
        json_str = '{"hello": "world", "data": [1,2,3]}'
        expected = {"hello": "world", "data": [1, 2, 3]}
        loader = jsondiff.JsonLoader()
        actual = loader(json_str)
        self.assertEqual(expected, actual)

    def test_json_file_loader(self):
        json_file = os.path.join(TestLoaders.data_dir, "test_01.json")
        expected = {"hello": "world", "data": [1, 2, 3]}
        loader = jsondiff.JsonLoader()
        with open(json_file) as f:
            actual = loader(f)
        self.assertEqual(expected, actual)

    def test_yaml_string_loader(self):
        json_str = """---
hello: world
data:
  - 1
  - 2
  - 3
        """
        expected = {"hello": "world", "data": [1, 2, 3]}
        loader = jsondiff.YamlLoader()
        actual = loader(json_str)
        self.assertEqual(expected, actual)

    def test_yaml_file_loader(self):
        yaml_file = os.path.join(TestLoaders.data_dir, "test_01.yaml")
        expected = {"hello": "world", "data": [1, 2, 3]}
        loader = jsondiff.YamlLoader()
        with open(yaml_file) as f:
            actual = loader(f)
        self.assertEqual(expected, actual)


class TestDumpers(unittest.TestCase):

    def test_json_dump_string(self):
        data = {"hello": "world", "data": [1, 2, 3]}
        expected = '{"hello": "world", "data": [1, 2, 3]}'
        dumper = jsondiff.JsonDumper()
        actual = dumper(data)
        self.assertEqual(expected, actual)

    def test_json_dump_string_indented(self):
        data = {"hello": "world", "data": [1, 2, 3]}
        expected = """{
    "hello": "world",
    "data": [
        1,
        2,
        3
    ]
}"""
        dumper = jsondiff.JsonDumper(indent=4)
        actual = dumper(data)
        self.assertEqual(expected, actual)

    def test_json_dump_string_fp(self):
        data = {"hello": "world", "data": [1, 2, 3]}
        expected = """{
    "hello": "world",
    "data": [
        1,
        2,
        3
    ]
}"""
        dumper = jsondiff.JsonDumper(indent=4)
        buffer = io.StringIO()
        dumper(data, buffer)
        self.assertEqual(expected, buffer.getvalue())

    def test_yaml_dump_string(self):
        data = {"hello": "world", "data": [1, 2, 3]}
        expected = """data:
- 1
- 2
- 3
hello: world
"""
        # Sort keys just to make things deterministic
        dumper = jsondiff.YamlDumper(sort_keys=True)
        actual = dumper(data)
        self.assertEqual(expected, actual)

    def test_yaml_dump_string_fp(self):
        data = {"hello": "world", "data": [1, 2, 3]}
        expected = """data:
- 1
- 2
- 3
hello: world
"""
        # Sort keys just to make things deterministic
        dumper = jsondiff.YamlDumper(sort_keys=True)
        buffer = io.StringIO()
        dumper(data, buffer)
        self.assertEqual(expected, buffer.getvalue())

    def test_exclude_paths(self):
        differ = JsonDiffer()

        a = {'a': 1, 'b': {'b1': 20, 'b2': 21}, 'c': 3}
        b = {'a': 1, 'b': {'b1': 22, 'b2': 23}, 'c': 30}

        exclude_paths = ['b.b1', 'c']

        d = differ.diff(a, b, exclude_paths=exclude_paths)

        # The diff should only contain changes that are not in the exclude_paths
        self.assertEqual({'b': {'b2': 23}}, d)

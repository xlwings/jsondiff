__version__ = '0.1.0'

import sys
import json

from .symbols import *
from .symbols import Symbol

# rules
# - keys and strings which start with $ are escaped to $$
# - when source is dict and diff is a dict -> patch
# - when source is list and diff is a list patch dict -> patch
# - else -> replacement

# Python 2 vs 3
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str
else:
    string_types = basestring


class JsonDumper(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, obj, dest=None):
        if dest is None:
            return json.dumps(obj, **self.kwargs)
        else:
            return json.dump(obj, dest, **self.kwargs)


class JsonLoader(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, src):
        if isinstance(src, string_types):
            return json.loads(src, **self.kwargs)
        else:
            return json.load(src, **self.kwargs)


class JsonDiffSyntax(object):
    def emit_set_diff(self, a, b, s, added, removed):
        raise NotImplementedError()

    def emit_list_diff(self, a, b, s, inserted, changed, deleted):
        raise NotImplementedError()

    def emit_dict_diff(self, a, b, s, added, changed, removed):
        raise NotImplementedError()

    def emit_value_diff(self, a, b, s):
        raise NotImplementedError()


class CompactJsonDiffSyntax(object):
    def emit_set_diff(self, a, b, s, added, removed):
        if s == 0.0 or len(removed) == len(a):
            return b
        else:
            d = {}
            if removed:
                d[discard] = removed
            if added:
                d[add] = added
            return d

    def emit_list_diff(self, a, b, s, inserted, changed, deleted):
        if s == 0.0:
            return b
        elif s == 1.0:
            return {}
        else:
            d = changed
            if inserted:
                d[insert] = inserted
            if deleted:
                d[delete] = deleted
            return d

    def emit_dict_diff(self, a, b, s, added, changed, removed):
        if s == 0.0:
            return {replace: b}
        elif s == 1.0:
            return {}
        else:
            changed.update(added)
            if removed:
                changed[delete] = list(removed.keys())
            return changed

    def emit_value_diff(self, a, b, s):
        if s == 1.0:
            return {}
        else:
            return b


class ExplicitJsonDiffSyntax(object):
    def emit_set_diff(self, a, b, s, added, removed):
        if s == 0.0 or len(removed) == len(a):
            return b
        else:
            d = {}
            if removed:
                d[discard] = removed
            if added:
                d[add] = added
            return d

    def emit_list_diff(self, a, b, s, inserted, changed, deleted):
        if s == 0.0:
            return b
        elif s == 1.0:
            return {}
        else:
            d = changed
            if inserted:
                d[insert] = inserted
            if deleted:
                d[delete] = deleted
            return d

    def emit_dict_diff(self, a, b, s, added, changed, removed):
        if s == 0.0:
            return b
        elif s == 1.0:
            return {}
        else:
            d = {}
            if added:
                d[insert] = added
            if changed:
                d[update] = changed
            if removed:
                d[delete] = removed
            return d

    def emit_value_diff(self, a, b, s):
        if s == 1.0:
            return {}
        else:
            return b


class SymmetricJsonDiffSyntax(object):
    def emit_set_diff(self, a, b, s, added, removed):
        if s == 0.0 or len(removed) == len(a):
            return {left: a, right: b}
        else:
            d = {}
            if added:
                d[right] = added
            if removed:
                d[left] = removed
            return d

    def emit_list_diff(self, a, b, s, inserted, changed, deleted):
        if s == 0.0:
            return b
        elif s == 1.0:
            return {}
        else:
            d = changed
            if inserted:
                d[insert] = inserted
            if deleted:
                d[delete] = deleted
            return d

    def emit_dict_diff(self, a, b, s, added, changed, removed):
        if s == 0.0:
            return {left: a, right: b}
        elif s == 1.0:
            return {}
        else:
            d = {}
            if added:
                d[right] = added
            if changed:
                d[update] = changed
            if removed:
                d[left] = removed
            return d

    def emit_value_diff(self, a, b, s):
        if s == 1.0:
            return {}
        else:
            return {left: a, right: b}


builtin_syntaxes = {
    'compact': CompactJsonDiffSyntax(),
    'symmetric': SymmetricJsonDiffSyntax(),
    'explicit': ExplicitJsonDiffSyntax()
}


class JsonDiffer(object):

    def __init__(self, syntax='compact'):
        if isinstance(syntax, string_types):
            syntax = builtin_syntaxes[syntax]
        self._syntax = syntax
        self._symbol_map = {
            symbol.label: symbol
            for symbol in (add, discard, insert, delete, update)
        }

    def _list_diff_0(self, C, X, Y, i, j):
        if i > 0 and j > 0:
            d, s = self._obj_diff(X[i-1], Y[j-1])
            if s > 0 and C[i][j] == C[i-1][j-1] + s:
                for annotation in self._list_diff_0(C, X, Y, i-1, j-1):
                    yield annotation
                yield (0, d, j-1, s)
                return
        if j > 0 and (i == 0 or C[i][j-1] >= C[i-1][j]):
            for annotation in self._list_diff_0(C, X, Y, i, j-1):
                yield annotation
            yield (1, Y[j-1], j-1, 0.0)
            return
        if i > 0 and (j == 0 or C[i][j-1] < C[i-1][j]):
            for annotation in self._list_diff_0(C, X, Y, i-1, j):
                yield annotation
            yield (-1, X[i-1], i-1, 0.0)
            return

    def _list_diff(self, X, Y):
        # LCS
        m = len(X)
        n = len(Y)
        # An (m+1) times (n+1) matrix
        C = [[0 for j in range(n+1)] for i in range(m+1)]
        for i in range(1, m+1):
            for j in range(1, n+1):
                _, s = self._obj_diff(X[i-1], Y[j-1])
                # Following lines are part of the original LCS algorithm
                # left in the code in case modification turns out to be problematic
                #if X[i-1] == Y[j-1]:
                #    C[i][j] = C[i-1][j-1] + 1
                #else:
                C[i][j] = max(C[i][j-1], C[i-1][j], C[i-1][j-1] + s)
        inserted = []
        deleted = []
        changed = {}
        tot_s = 0.0
        for sign, value, pos, s in self._list_diff_0(C, X, Y, len(X), len(Y)):
            if sign == 1:
                inserted.append((pos, value))
            elif sign == -1:
                deleted.append(pos)
            elif sign == 0 and s < 1:
                changed[pos] = value
            tot_s += s
        tot_n = len(X) + len(inserted)
        if tot_n == 0:
            s = 1.0
        else:
            s = tot_s / tot_n
        return self._syntax.emit_list_diff(X, Y, s, inserted, changed, deleted), s

    def _set_diff(self, a, b):
        removed = a.difference(b)
        added = b.difference(a)
        if not removed and not added:
            return {}, 1.0
        ranking = sorted(
            (
                (self._obj_diff(x, y)[1], x, y)
                for x in removed
                for y in added
            ),
            reverse=True
        )
        r2 = set(removed)
        a2 = set(added)
        n_common = len(a) - len(removed)
        s_common = float(n_common)
        for s, x, y in ranking:
            if x in r2 and y in a2:
                r2.discard(x)
                a2.discard(y)
                s_common += s
                n_common += 1
            if not r2 or not a2:
                break
        n_tot = len(a) + len(added)
        s = s_common / n_tot if n_tot != 0 else 1.0
        return self._syntax.emit_set_diff(a, b, s, added, removed), s

    def _dict_diff(self, a, b):
        removed = {}
        nremoved = 0
        nadded = 0
        nmatched = 0
        smatched = 0.0
        added = {}
        changed = {}
        for k, v in a.items():
            w = b.get(k, missing)
            if w is missing:
                nremoved += 1
                removed[k] = v
            else:
                nmatched += 1
                d, s = self._obj_diff(v, w)
                if s < 1.0:
                    changed[k] = d
                smatched += 0.5 + 0.5 * s
        for k, v in b.items():
            if k not in a:
                nadded += 1
                added[k] = v
        n_tot = nremoved + nmatched + nadded
        s = smatched / n_tot if n_tot != 0 else 1.0
        return self._syntax.emit_dict_diff(a, b, s, added, changed, removed), s

    def _obj_diff(self, a, b):
        if a is b:
            return self._syntax.emit_value_diff(a, b, 1.0), 1.0
        if type(a) is dict and type(b) is dict:
            return self._dict_diff(a, b)
        elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            return self._list_diff(a, b)
        elif isinstance(a, set) and isinstance(b, set):
            return self._set_diff(a, b)
        elif a != b:
            return self._syntax.emit_value_diff(a, b, 0.0), 0.0
        else:
            return self._syntax.emit_value_diff(a, b, 1.0), 1.0

    def diff(self, a, b):
        return self._obj_diff(a, b)

    def _unescape(self, x):
        if isinstance(x, string_types):
            sym = self._symbol_map.get(x, None)
            if sym is not None:
                return sym
            if x.startswith('$'):
                return x[1:]
        return x

    def unmarshal(self, d):
        if isinstance(d, dict):
            return {
                self._unescape(k): self.unmarshal(v)
                for k, v in d.items()
            }
        elif isinstance(d, (list, tuple)):
            return [
                self.marshal(x)
                for x in d
            ]
        else:
            return self._unescape(d)

    def _escape(self, o):
        if type(o) is Symbol:
            return "$" + o.label
        if isinstance(o, string_types) and o.startswith('$'):
            return "$" + o
        return o

    def marshal(self, d):
        if isinstance(d, dict):
            return {
                self._escape(k): self.marshal(v)
                for k, v in d.items()
            }
        elif isinstance(d, (list, tuple)):
            return [
                self.marshal(x)
                for x in d
            ]
        else:
            return self._escape(d)


default_differ = JsonDiffer()

default_dumper = JsonDumper()

default_loader = JsonLoader()


def diff(a, b, differ=default_differ, load=False, dump=False, marshal=False, loader=default_loader, dumper=default_dumper):
    if load:
        a = loader(a)
        b = loader(b)

    d, s = differ.diff(a, b)

    if dump or marshal:
        d = differ.marshal(d)

    if dump:
        return dumper(d, None if dump is True else dump)
    else:
        return d


def similarity(a, b, differ=default_differ):
    d, s = differ.diff(a, b)
    return s


__all__ = [
    "similarity",
    "diff",
    "dump",
    "dumps",
    "load",
    "loads"
]

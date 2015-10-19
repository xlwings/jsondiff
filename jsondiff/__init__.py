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


def list_diff_0(C, X, Y, i, j):
    if i > 0 and j > 0:
        d, s = obj_diff(X[i-1], Y[j-1])
        if s > 0 and C[i][j] == C[i-1][j-1] + s:
            for annotation in list_diff_0(C, X, Y, i-1, j-1):
                yield annotation
            yield (0, d, j-1, s)
            return
    if j > 0 and (i == 0 or C[i][j-1] >= C[i-1][j]):
        for annotation in list_diff_0(C, X, Y, i, j-1):
            yield annotation
        yield (1, Y[j-1], j-1, 0.0)
        return
    if i > 0 and (j == 0 or C[i][j-1] < C[i-1][j]):
        for annotation in list_diff_0(C, X, Y, i-1, j):
            yield annotation
        yield (-1, X[i-1], i-1, 0.0)
        return


def list_diff(X, Y):
    # LCS
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0 for j in range(n+1)] for i in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            _, s = obj_diff(X[i-1], Y[j-1])
            # Following lines are part of the original LCS algorithm
            # left in the code in case modification turns out to be problematic
            #if X[i-1] == Y[j-1]:
            #    C[i][j] = C[i-1][j-1] + 1
            #else:
            C[i][j] = max(C[i][j-1], C[i-1][j], C[i-1][j-1] + s)
    inserted = []
    deleted = []
    changed = []
    tot_s = 0.0
    for sign, value, pos, s in list_diff_0(C, X, Y, len(X), len(Y)):
        if sign == 1:
            inserted.append((pos, value))
        elif sign == -1:
            deleted.append(pos)
        elif sign == 0 and s < 1:
            changed.append((pos, value))
        tot_s += s
    s = tot_s / (len(X) + len(inserted))
    if s == 0.0:
        return Y, 0.0
    elif s == 1.0:
        return identical, 1.0
    else:
        d = {}
        if inserted:
            d[insert] = inserted
        if deleted:
            d[delete] = deleted
        if changed:
            d[update] = changed
        return d, s


def set_diff(a, b):
    removed = a.difference(b)
    added = b.difference(a)
    if not removed and not added:
        return identical, 1.0
    ranking = sorted(
        (
            (obj_diff(x, y)[1], x, y)
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
    s = s_common / (len(a) + len(added))
    if s == 0.0 or len(removed) == len(a):
        return b, 0.0
    else:
        d = {}
        if removed:
            d[discard] = removed
        if added:
            d[add] = added
        return d, s


def dict_diff(a, b):
    removed = []
    nremoved = 0
    nadded = 0
    nmatched = 0
    smatched = 0.0
    changed = {}
    added = {}
    for k, v in a.items():
        w = b.get(k, missing)
        if w is missing:
            nremoved += 1
            removed.append(k)
        else:
            nmatched += 1
            d, s = obj_diff(v, w)
            if s < 1.0:
                changed[k] = d
            smatched += s
    for k, v in b.items():
        if k not in a:
            nadded += 1
            added[k] = v
    s = smatched / (nremoved + nmatched + nadded)
    if s == 0.0:
        return b, 0.0
    elif s == 1.0:
        return identical, 1.0
    else:
        d = {}
        if added:
            d[insert] = added
        if changed:
            d[update] = changed
        if removed:
            d[delete] = removed
        return d, s


def obj_diff(a, b):
    if a is b:
        return identical, 1.0
    if type(a) is dict and type(b) is dict:
        return dict_diff(a, b)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return list_diff(a, b)
    elif isinstance(a, set) and isinstance(b, set):
        return set_diff(a, b)
    elif a != b:
        return b, 0.0
    else:
        return identical, 1.0


class DiffEncoder(json.JSONEncoder):

    def _escape(self, o):
        if type(o) is Symbol:
            return "$" + o.label
        if isinstance(o, string_types) and o.startswith('$'):
            return "$" + o
        return o

    def encode(self, o):
        if type(o) is dict:
            o = {
                self._escape(k): v
                for k, v in o.iteritems()
            }
        else:
            o = self._escape(o)
        return super(DiffEncoder, self).encode(o)


class DiffDecoder(json.JSONDecoder):
    _symbol_map = {
        "$" + symbol.label: symbol
        for symbol in (add, discard, insert, delete, update, identical)
    }

    def _unescape(self, o):
        if isinstance(o, string_types):
            sym = DiffDecoder._symbol_map.get(o, None)
            if sym is not None:
                return sym
            if o.startswith('$'):
                return o[1:]
        return o

    def decode(self, s, *args, **kwargs):
        o = super(DiffDecoder, self).decode(s, *args, **kwargs)
        if type(o) is dict:
            o = {
                self._unescape(k): v
                for k, v in o.iteritems()
            }
        else:
            o = self._unescape(o)
        return o


def similarity(a, b):
    return obj_diff(a, b)[1]


def dump(d, f=None, indent=None):
    if f is None:
        return json.dumps(d, indent=indent, cls=DiffEncoder)
    else:
        return json.dump(d, f, indent=indent, cls=DiffEncoder)

__dump = dump

dumps = dump


def load(f):
    if isinstance(f, string_types):
        return json.loads(f, cls=DiffDecoder)
    else:
        return json.load(f, cls=DiffDecoder)

loads = load


def diff(a, b, parse=False, dump=False, indent=None):
    if parse:
        if isinstance(a, string_types):
            a = json.loads(a)
        else:
            a = json.load(a)
        if isinstance(b, string_types):
            b = json.loads(b)
        else:
            b = json.load(b)
    d, s = obj_diff(a, b)
    if dump:
        if dump is True:
            return __dump(d, indent=indent)
        else:
            return __dump(d, dump, indent=indent)
    else:
        return d


__all__ = [
    "similarity",
    "diff",
    "dump",
    "dumps",
    "load",
    "loads"
]

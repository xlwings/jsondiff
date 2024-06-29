class Symbol:
    def __init__(self, label):
        self._label = label

    @property
    def label(self):
        return self._label

    def __repr__(self):
        return self.label

    def __str__(self):
        return "$" + self.label

    def __eq__(self, other):
        return self.label == other.label
    
    def __hash__(self) -> int:
        return hash(self.label)


missing = Symbol('missing')
identical = Symbol('identical')
delete = Symbol('delete')
insert = Symbol('insert')
update = Symbol('update')
add = Symbol('add')
discard = Symbol('discard')
replace = Symbol('replace')
left = Symbol('left')
right = Symbol('right')

_all_symbols_ = [
    missing,
    identical,
    delete,
    insert,
    update,
    add,
    discard,
    replace,
    left,
    right
]

__all__ = [
    'missing',
    'identical',
    'delete',
    'insert',
    'update',
    'add',
    'discard',
    'replace',
    'left',
    'right',
    '_all_symbols_'
]


class Symbol(object):
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return self.label

    def __str__(self):
        return "$" + self.label

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
    'right'
]
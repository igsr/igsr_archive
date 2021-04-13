#OrderedDict
An OrderedDict is a dictionary subclass that remembers the order in which its contents are added.

import collections

print 'Regular dictionary:'
d = {}
d['a'] = 'A'
d['b'] = 'B'
d['c'] = 'C'
d['d'] = 'D'
d['e'] = 'E'

for k, v in d.items():
    print k, v

print '\nOrderedDict:'
d = collections.OrderedDict()
d['a'] = 'A'
d['b'] = 'B'
d['c'] = 'C'
d['d'] = 'D'
d['e'] = 'E'

for k, v in d.items():
    print k, v

A regular dict does not track the insertion order, and iterating over it produces the values in an arbitrary order. In an OrderedDict, by contrast, 
the order the items are inserted is remembered and used when creating an iterator.
$ python collections_ordereddict_iter.py

Regular dictionary:
a A
c C
b B
e E
d D

OrderedDict:
a A
b B
c C
d D
e E

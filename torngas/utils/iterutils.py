#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys ,traceback ,time
from torngas.utils.storage import storage


class Counter(storage):
    """Keeps count of how many times something is added.

        >>> c = counter()
        >>> c.add('x')
        >>> c.add('x')
        >>> c.add('x')
        >>> c.add('x')
        >>> c.add('x')
        >>> c.add('y')
        >>> c
        <Counter {'y': 1, 'x': 5}>
        >>> c.most()
        ['x']
    """

    def add(self, n):
        self.setdefault(n, 0)
        self[n] += 1

    def most(self):
        """Returns the keys with maximum count."""
        m = max(self.itervalues())
        return [k for k, v in self.iteritems() if v == m]

    def least(self):
        """Returns the keys with mininum count."""
        m = min(self.itervalues())
        return [k for k, v in self.iteritems() if v == m]

    def percent(self, key):
        """Returns what percentage a certain key is of all entries.

            >>> c = counter()
            >>> c.add('x')
            >>> c.add('x')
            >>> c.add('x')
            >>> c.add('y')
            >>> c.percent('x')
            0.75
            >>> c.percent('y')
            0.25
        """
        return float(self[key]) / sum(self.values())

    def sorted_keys(self):
        """Returns keys sorted by value.

             >>> c = counter()
             >>> c.add('x')
             >>> c.add('x')
             >>> c.add('y')
             >>> c.sorted_keys()
             ['x', 'y']
        """
        return sorted(self.keys(), key=lambda k: self[k], reverse=True)

    def sorted_values(self):
        """Returns values sorted by value.

            >>> c = counter()
            >>> c.add('x')
            >>> c.add('x')
            >>> c.add('y')
            >>> c.sorted_values()
            [2, 1]
        """
        return [self[k] for k in self.sorted_keys()]

    def sorted_items(self):
        """Returns items sorted by value.

            >>> c = counter()
            >>> c.add('x')
            >>> c.add('x')
            >>> c.add('y')
            >>> c.sorted_items()
            [('x', 2), ('y', 1)]
        """
        return [(k, self[k]) for k in self.sorted_keys()]

    def __repr__(self):
        return '<Counter ' + dict.__repr__(self) + '>'


counter = Counter

iters = [list, tuple]
import __builtin__

if hasattr(__builtin__, 'set'):
    iters.append(set)
if hasattr(__builtin__, 'frozenset'):
    iters.append(set)
if sys.version_info < (2, 6): # sets module deprecated in 2.6
    try:
        from sets import Set

        iters.append(Set)
    except ImportError:
        pass


class _hack(tuple): pass


iters = _hack(iters)
iters.__doc__ = """
A list of iterable items (like lists, but not strings). Includes whichever
of lists, tuples, sets, and Sets are available in this version of Python.
"""

def group(seq, size):
    """
    Returns an iterator over a series of lists of length size from iterable.

        >>> list(group([1,2,3,4], 2))
        [[1, 2], [3, 4]]
        >>> list(group([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """

    def take(seq, n):
        for i in xrange(n):
            yield seq.next()

    if not hasattr(seq, 'next'):
        seq = iter(seq)
    while True:
        x = list(take(seq, size))
        if x:
            yield x
        else:
            break


def uniq(seq, key=None):
    """
    Removes duplicate elements from a list while preserving the order of the rest.

        >>> uniq([9,0,2,1,0])
        [9, 0, 2, 1]

    The value of the optional `key` parameter should be a function that
    takes a single argument and returns a key to test the uniqueness.

        >>> uniq(["Foo", "foo", "bar"], key=lambda s: s.lower())
        ['Foo', 'bar']
    """
    key = key or (lambda x: x)
    seen = set()
    result = []
    for v in seq:
        k = key(v)
        if k in seen:
            continue
        seen.add(k)
        result.append(v)
    return result


def iterview(x):
    """
    Takes an iterable `x` and returns an iterator over it
    which prints its progress to stderr as it iterates through.
    """
    WIDTH = 70

    def plainformat(n, lenx):
        return '%5.1f%% (%*d/%d)' % ((float(n) / lenx) * 100, len(str(lenx)), n, lenx)

    def bars(size, n, lenx):
        val = int((float(n) * size) / lenx + 0.5)
        if size - val:
            spacing = ">" + (" " * (size - val))[1:]
        else:
            spacing = ""
        return "[%s%s]" % ("=" * val, spacing)

    def eta(elapsed, n, lenx):
        if n == 0:
            return '--:--:--'
        if n == lenx:
            secs = int(elapsed)
        else:
            secs = int((elapsed / n) * (lenx - n))
        mins, secs = divmod(secs, 60)
        hrs, mins = divmod(mins, 60)

        return '%02d:%02d:%02d' % (hrs, mins, secs)

    def format(starttime, n, lenx):
        out = plainformat(n, lenx) + ' '
        if n == lenx:
            end = '     '
        else:
            end = ' ETA '
        end += eta(time.time() - starttime, n, lenx)
        out += bars(WIDTH - len(out) - len(end), n, lenx)
        out += end
        return out

    starttime = time.time()
    lenx = len(x)
    for n, y in enumerate(x):
        sys.stderr.write('\r' + format(starttime, n, lenx))
        yield y
    sys.stderr.write('\r' + format(starttime, n + 1, lenx) + '\n')


class IterBetter:
    """
    Returns an object that can be used as an iterator
    but can also be used via __getitem__ (although it
    cannot go backwards -- that is, you cannot request
    `iterbetter[0]` after requesting `iterbetter[1]`).

        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3

    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.

        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []
    """

    def __init__(self, iterator):
        self.i, self.c = iterator, 0

    def __iter__(self):
        if hasattr(self, "_head"):
            yield self._head

        while 1:
            yield self.i.next()
            self.c += 1

    def __getitem__(self, i):
        #todo: slices
        if i < self.c:
            raise IndexError, "already passed " + str(i)
        try:
            while i > self.c:
                self.i.next()
                self.c += 1
                # now self.c == i
            self.c += 1
            return self.i.next()
        except StopIteration:
            raise IndexError, str(i)

    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return len(self) != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = self.i.next()
            except StopIteration:
                return False
            else:
                return True


iterbetter = IterBetter


def safeiter(it, cleanup=None, ignore_errors=True):
    """Makes an iterator safe by ignoring the exceptions occured during the iteration.
    """

    def next():
        while True:
            try:
                return it.next()
            except StopIteration:
                raise
            except:
                traceback.print_exc()

    it = iter(it)
    while True:
        yield next()


def dictreverse(mapping):
    """
    Returns a new dictionary with keys and values swapped.

        >>> dictreverse({1: 2, 3: 4})
        {2: 1, 4: 3}
    """
    return dict([(value, key) for (key, value) in mapping.iteritems()])


def dictfind(dictionary, element):
    """
    Returns a key whose value in `dictionary` is `element`
    or, if none exists, None.

        >>> d = {1:2, 3:4}
        >>> dictfind(d, 4)
        3
        >>> dictfind(d, 5)
    """
    for (key, value) in dictionary.iteritems():
        if element is value:
            return key


def dictfindall(dictionary, element):
    """
    Returns the keys whose values in `dictionary` are `element`
    or, if none exists, [].

        >>> d = {1:4, 3:4}
        >>> dictfindall(d, 4)
        [1, 3]
        >>> dictfindall(d, 5)
        []
    """
    res = []
    for (key, value) in dictionary.iteritems():
        if element is value:
            res.append(key)
    return res


def dictincr(dictionary, element):
    """
    Increments `element` in `dictionary`,
    setting it to one if it doesn't exist.

        >>> d = {1:2, 3:4}
        >>> dictincr(d, 1)
        3
        >>> d[1]
        3
        >>> dictincr(d, 5)
        1
        >>> d[5]
        1
    """
    dictionary.setdefault(element, 0)
    dictionary[element] += 1
    return dictionary[element]


def dictadd(*dicts):
    """
    Returns a dictionary consisting of the keys in the argument dictionaries.
    If they share a key, the value from the last argument is used.

        >>> dictadd({1: 0, 2: 0}, {2: 1, 3: 1})
        {1: 0, 2: 1, 3: 1}
    """
    result = {}
    for dct in dicts:
        result.update(dct)
    return result


def requeue(queue, index=-1):
    """Returns the element at index after moving it to the beginning of the queue.

        >>> x = [1, 2, 3, 4]
        >>> requeue(x)
        4
        >>> x
        [4, 1, 2, 3]
    """
    x = queue.pop(index)
    queue.insert(0, x)
    return x


def restack(stack, index=0):
    """Returns the element at index after moving it to the top of stack.

           >>> x = [1, 2, 3, 4]
           >>> restack(x)
           1
           >>> x
           [2, 3, 4, 1]
    """
    x = stack.pop(index)
    stack.append(x)
    return x


def listget(lst, ind, default=None):
    """
    Returns `lst[ind]` if it exists, `default` otherwise.

        >>> listget(['a'], 0)
        'a'
        >>> listget(['a'], 1)
        >>> listget(['a'], 1, 'b')
        'b'
    """
    if len(lst) - 1 < ind:
        return default
    return lst[ind]



# -*- coding: utf-8 -*-

# Copyright (c) 203 Javier Escalada Gómez
# All rights reserved.
# License: BSD 3-Clause Clear License (see LICENSE for details)

"""
This module provides several functions to work with nested collections of data.
One example of nested collections are JSON-like objects.

It provides functions to manipulate the values of nested collection using a path-like notation.
A path is a sequence of keys and indices that can be used to access a value.

>>> obj = {"a": [{"b": 1}, {"b": 2}], "c": [{"d": 10}, {"d": 20}]}
>>> get(obj, ("c", 0, "d"))
10
>>> set(obj, ("c", 0, "d"), 100)
{'a': [{'b': 1}, {'b': 2}], 'c': [{'d': 100}, {'d': 20}]}
>>> delete(obj, ("c",))
{'a': [{'b': 1}, {'b': 2}]}

It also provides functions to convert a nested collection into a flatten collection and vice versa.
This allows to use standard higher-order functions (or similar tools) to manipulate the values.

>>> paths = list(flatten(obj))
>>> paths
[((), {}), (('a',), []), (('a', 0), {}), (('a', 1), {}), (('a', 0, 'b'), 1), (('a', 1, 'b'), 2)]
>>> updates = [(path, value * 10)
...   for path, value in paths
...   if fullmatch(path, ("a", ..., "b"))]
>>> updates
[(('a', 0, 'b'), 10), (('a', 1, 'b'), 20)]
>>> for path, value in updates: set(obj, path, value)
{'a': [{'b': 10}, {'b': 2}]}
{'a': [{'b': 10}, {'b': 20}]}
>>> obj
{'a': [{'b': 10}, {'b': 20}]}
>>> unflatten(flatten(obj))
{'a': [{'b': 10}, {'b': 20}]}
"""

__author__ = "Javier Escalada Gómez"
__email__ = "kerrigan29a@gmail.com"
__version__ = "0.1.0"
__license__ = "BSD 3-Clause Clear License"

from collections.abc import Mapping, Iterable
from collections import deque

_undefined = object()


def get(obj, path, default=_undefined):
    """ Get a value from a nested collection using the path.

    >>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
    >>> get(obj, ("a", 0, "b", "c"))
    10
    >>> get(obj, ("a", 1, "b", "c"))
    100

    If the path does not exist, an exception is raised.

    >>> get(obj, ("a", 2, "b", "c"))
    Traceback (most recent call last):
        ...
    IndexError: list index out of range

    It is possible to provide a default value to return in case the path does not exist.

    >>> get(obj, ("a", 2, "b", "c"), "default")
    'default'
    >>> get(obj, ("a",))
    [{'b': {'c': 10}}, {'b': {'c': 100}}]
    """
    if not path:
        return obj
    try:
        return _traverse(obj, path)
    except (KeyError, IndexError) as e:
        if default is _undefined:
            raise e
        return default


def set(obj, path, value):
    """ Modify a value.

    This is useful to modify a value in an object or to insert a new value in a dict-like object. 

    >>> obj = {"a": [{"b": 1}, {"b": 2}]}
    >>> set(obj, ("a", 0, "b"), 10)
    {'a': [{'b': 10}, {'b': 2}]}

    To append a new value in a list-like object, use as index the length of the list at the moment of the insertion.

    >>> obj = {"a": []}
    >>> set(obj, ("a", 0), {})
    {'a': [{}]}
    >>> set(obj, ("a", 1), {})
    {'a': [{}, {}]}
    >>> set(obj, ("a", 0, "b"), 1)
    {'a': [{'b': 1}, {}]}
    >>> set(obj, ("a", -1, "b"), 2)
    {'a': [{'b': 1}, {'b': 2}]}

    This function returns the object with the new value.
    """
    if not path:
        raise ValueError("path must not be empty")
    cur = _traverse(obj, path[:-1])
    try:
        cur[path[-1]] = value
    except IndexError as e:
        if path[-1] == len(cur):
            cur.append(value)
        else:
            raise e
    return obj


def delete(obj, path):
    """ Delete a value.

    Deleting the last value in an object does not delete that object.

    >>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
    >>> delete(obj, ["a", 0, "b", "c"])
    {'a': [{'b': {}}, {'b': {'c': 100}}]}
    >>> delete(obj, ["a", 1, "b", "c"]) 
    {'a': [{'b': {}}, {'b': {}}]}
    >>> delete(obj, ["a", 2, "b"])
    Traceback (most recent call last):
    ...
    IndexError: list index out of range
    >>> delete(obj, ["a", 1, "c"])
    Traceback (most recent call last):
    ...
    KeyError: 'c'

    This function returns the object with the deleted value.
    """
    if not path:
        raise ValueError("path must not be empty")
    cur = _traverse(obj, path[:-1])
    try:
        del cur[path[-1]]
    except KeyError as e:
        raise e
    except IndexError as e:
        raise e
    return obj


def update(obj, path, func):
    """ Update a value based on the current value.

    This is an efficient alternative to getting a value, modifying it and setting it back.

    >>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
    >>> update(obj, ["a", 0, "b", "c"], lambda x: x + 1)
    {'a': [{'b': {'c': 11}}, {'b': {'c': 100}}]}
    >>> update(obj, ["a", 1, "b", "c"], lambda x: x + 1)
    {'a': [{'b': {'c': 11}}, {'b': {'c': 101}}]}
    >>> update(obj, ["a", 2, "b", "c"], lambda x: x + 1)
    Traceback (most recent call last):
    ...
    IndexError: list index out of range

    This function returns the updated object.
    """
    if not path:
        raise ValueError("path must not be empty")
    cur = _traverse(obj, path[:-1])
    try:
        cur[path[-1]] = func(cur[path[-1]])
    except (KeyError, IndexError) as e:
        raise e
    return obj


def _traverse(obj, path):
    if isinstance(path, str) or not isinstance(path, Iterable):
        raise TypeError("path must be an iterable of keys")
    for key in path:
        try:
            obj = obj[key]
        except (KeyError, IndexError) as e:
            raise e
    return obj


def flatten(obj, only_leaves=False):
    """ Flatten (or [data_tools.unnest]) a nested object.

    This functions returns all the paths in the tree structure of the object.

    >>> list(flatten({'a': 1, 'b': 1}))
    [((), {}), (('a',), 1), (('b',), 1)]
    >>> list(flatten({'a': {'B': 1}, 'b': {'B': 1}}))
    [((), {}), (('a',), {}), (('b',), {}), (('a', 'B'), 1), (('b', 'B'), 1)]

    By default, it also returns the non-leaf nodes.
    This is useful to reconstruct the object using the [data_tools.unflatten] function.

    Set `only_leaves` to `True` to only return the leaves.
    This can be used to generate a CSV-like structure.

    >>> list(flatten({'a': {'B': 1}, 'b': {'B': 1}}, only_leaves=True))
    [(('a', 'B'), 1), (('b', 'B'), 1)]

    >>> list(flatten({'a': [{'b': 1}, {'b': 2}]}, only_leaves=False))
    [((), {}), (('a',), []), (('a', 0), {}), (('a', 1), {}), (('a', 0, 'b'), 1), (('a', 1, 'b'), 2)]
    """
    if not obj:
        return
    queue = deque([(obj, [])])
    while queue:
        obj, path = queue.popleft()
        if isinstance(obj, Mapping):
            if not only_leaves:
                yield tuple(path), obj.__class__()
            for key, value in obj.items():
                queue.append((value, [*path, key]))
        elif isinstance(obj, Iterable) and not isinstance(obj, str):
            if not only_leaves:
                yield tuple(path), obj.__class__()
            for i, value in enumerate(obj):
                queue.append((value, [*path, i]))
        else:
            yield tuple(path), obj


def unflatten(paths, sort=False):
    """ Unflatten (or [data_tools.unnest]) a list of paths.

    The expected input is a list of paths, as returned by the [data_tools.flatten] function.

    >>> unflatten([((), {}), (('a',), 1), (('b',), 1)])
    {'a': 1, 'b': 1}
    >>> unflatten([((), {}), (('a',), {}), (('a', 'B'), 1), (('b',), {}), (('b', 'B'), 1)])
    {'a': {'B': 1}, 'b': {'B': 1}}
    >>> unflatten([((), {}), (('a',), []), (('a', 0), {}), (('a', 0, 'b'), 1), (('a', 1), {}), (('a', 1, 'b'), 2)])
    {'a': [{'b': 1}, {'b': 2}]}

    Internally, this function sets each path in the given order to create the nested object.
    This means that the order of the paths matters.

    >>> unflatten([(('a', 0, 'b'), 1), (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), ((),{}), (('a'), [])])
    Traceback (most recent call last):
    ...
    ValueError: invalid root

    The first path must be a single element, which will be the root of the object.

    >>> unflatten([((), {}), (('a', 0, 'b'), 1) , (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), (('a',), [])])
    Traceback (most recent call last):
    ...
    KeyError: 'a'

    For setting the 0 index at `a`, there must be a list at `a`.
    One way to ensure this is to sort the paths by length.
    This way, the paths that set the intermediate values are processed first.

    >>> unflatten([((), {}), (('a', 0, 'b'), 1) , (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), (('a',), [])], sort=True)
    {'a': [{'b': 1}, {'b': 2}]}
    """
    if not paths:
        return None
    
    if sort:
        paths = sorted(paths, key=lambda x: len(x[0]))

    paths = iter(paths)
    root, base = next(paths)
    if len(root) != 0:
        raise ValueError("invalid root")
    obj = base
    for path, value in paths:
        if len(path) < 1:
            raise ValueError("invalid path")
        set(obj, path, value)
    return obj


def unnest(*args, **kwargs):
    """
    Alias for [data_tools.flatten]
    """
    return flatten(*args, **kwargs)


def nest(*args, **kwargs):
    """
    Alias for [data_tools.unflatten]
    """
    return unflatten(*args, **kwargs)


def match(path, *patterns, wildcard=...):
    """ Check for a match at the beginning of a path.

    >>> path = ["a", "b", "c"]
    >>> match(path, ["a"])
    True
    >>> match(path, ["a", "b"])
    True
    >>> match(path, ["a", "b", "c"])
    True
    >>> match(path, ["a", "b", "c", "d"])
    False

    The patterns can contain a wildcard, to match any value.
    By default, the wildcard is `...`, but it can be changed.

    >>> match(path, ["a", ...])
    True
    >>> match(path, [..., "b"])
    True
    >>> match(path, ["A", ...])
    False
    >>> match(path, [..., "B"])
    False

    When multiple patterns are given, it returns `True` if any of them matches.

    >>> match(path, ["a"], ["A"])
    True
    """
    return any(_match(path, pattern, False, wildcard) for pattern in patterns)


def fullmatch(path, *patterns, wildcard=...):
    """ Check for a match in the whole path.

    The semantics are the same as the [data_tools.match] function.
    
    >>> path = ("a", "b", "c")
    >>> fullmatch(path, ("a"))
    False
    >>> fullmatch(path, ("a", "b"))
    False
    >>> fullmatch(path, ("a", "b", "c"))
    True
    >>> fullmatch(path, ("a", "b", "c", "d"))
    False

    >>> fullmatch(path, ("a", ..., ...))
    True
    >>> fullmatch(path, (..., "b", ...))
    True
    >>> fullmatch(path, (..., ..., "c"))
    True
    >>> fullmatch(path, ("A", ..., ...))
    False
    >>> fullmatch(path, (..., "B", ...))
    False
    >>> fullmatch(path, (..., ..., "C"))
    False
    >>> fullmatch(path, ("A", ..., ..., ...))
    False

    >>> fullmatch(path, ("a", ..., ...), ("A", ..., ...))
    True
    """
    return any(_match(path, pattern, True, wildcard) for pattern in patterns)


def _match(path, pattern, full, wildcard):
    it = iter(path)
    for p in pattern:
        try:
            curr = next(it)
        except StopIteration:
            # Patterns are longer than path
            return False
        if p is wildcard:
            continue
        if p != curr:
            return False
    try:
        next(it)
        # Path is longer than pattern
        return not full
    except StopIteration:
        # Path is same length as pattern
        return True
    

def parse(path, sep=".", quote=None):
    """ Parse a path string into a sequence of keys and indices.
    The separator is `.` by default, but it can be changed.

    >>> parse("")
    ()
    >>> parse("a.b.c")
    ('a', 'b', 'c')
    >>> parse("a/b/c", sep="/")
    ('a', 'b', 'c')

    The trailing, leading and consecutive separators are ignored.

    >>> parse("a.b.")
    ('a', 'b')
    >>> parse(".a.b")
    ('a', 'b')
    >>> parse("a..b.c")
    ('a', 'b', 'c')

    If a quote character is found, the path is parsed as a string.
    The default quote characters are `"` and `'`, but they can be changed.
    This is useful for keys that contain the separator.

    >>> parse("a.b.c")
    ('a', 'b', 'c')
    >>> parse("'a.b'.c")
    ('a.b', 'c')
    >>> parse('"a.b".c')
    ('a.b', 'c')
    >>> parse("/a.b/.c", quote="/")
    ('a.b', 'c')

    The numeric parts are parsed as base 10 integers and the rest as strings.
    This can be avoided quoting the numeric parts.

    >>> parse("a.0.b.-1")
    ('a', 0, 'b', -1)
    >>> parse("a.'0'.b.-1")
    ('a', '0', 'b', -1)
    """

    quotes = [quote] if quote else ['"', "'"]
    result = []
    last = -1
    quote = None
    path += sep
    for i, c in enumerate(path):
        # State 1: Normal character
        if c == sep and not quote:
            part = path[last+1:i]
            if part:
                # Remove quotes
                if part[0] in quotes and part[0] == part[-1]:
                    part = part[1:-1]
                # Or parse as int if possible
                else:
                    try:
                        part = int(part)
                    except ValueError:
                        pass
                result.append(part)
            last = i
        # State 2: Opening quote
        elif not quote and c in quotes:
            quote = c
        # State 3: Closing quote
        elif quote == c:
            quote = None
    return tuple(result)
        


if __name__ == "__main__":
    import doctest
    result = doctest.testmod()
    exit(int(bool(result.failed)))

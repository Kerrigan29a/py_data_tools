# Module [data\_tools](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L1)
This package provides several functions to work with nested collections of data.
One example of nested collections is JSON-like objects.

It provides functions to manipulate the values of nested collections using a
path-like notation. A path is a sequence of keys (`str`) and indices (`int`)
that can be used to access a value.

```python
>>> obj = {"a": [{"b": 1}, {"b": 2}], "c": [{"d": 10}, {"d": 20}]}
>>> get(obj, ("c", 0, "d"))
10
>>> set(obj, ("c", 0, "d"), 100)
{'a': [{'b': 1}, {'b': 2}], 'c': [{'d': 100}, {'d': 20}]}
>>> delete(obj, ("c",))
{'a': [{'b': 1}, {'b': 2}]}
```

These functions also support string paths.

```python
>>> get(obj, "a.0.b")
1
```

It also provides functions to convert a nested collection into a flattened
collection and vice versa. This allows to use standard higher-order functions
(or similar tools) to manipulate the values.

```python
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
```

## Function [data\_tools.get](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L70)
```python
def get(obj, path, default=_undefined, autoparse=AUTOPARSE, **parse_args): ...
```
Get a value from a nested collection using the `path`.

```python
>>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
>>> get(obj, ("a", 0, "b", "c"))
10
>>> get(obj, ("a", 1, "b", "c"))
100
```

If the `path` does not exist, an exception is raised.

```python
>>> get(obj, ("a", 2, "b", "c"))
Traceback (most recent call last):
    ...
IndexError: list index out of range
```

It is possible to provide a default value to return in case the path does
not exist.

```python
>>> get(obj, ("a", 2, "b", "c"), "default")
'default'
```

If the given `path` is a string and `autoparse` is `True`, it is first
converted using the [data_tools.parse] function. Any additional keyword
arguments are passed to the [data_tools.parse] function.

```python
>>> get(obj, "a/0/b/c", sep_chr="/")
10
```

## Function [data\_tools.set](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L118)
```python
def set(obj, path, value, autoparse=AUTOPARSE, **parse_args): ...
```
Modify or append a `value`.

This is useful to modify a `value` in an object or to insert a new `value`
in a dict-like object.

```python
>>> obj = {"a": [{"b": 1}, {"b": 2}]}
>>> set(obj, ("a", 0, "b"), 10)
{'a': [{'b': 10}, {'b': 2}]}
>>> set(obj, ("z",), 100)
{'a': [{'b': 10}, {'b': 2}], 'z': 100}
```

To append a new `value` in a list-like object, use as index the length of
the list at the moment of the insertion.

```python
>>> obj = {"a": []}
>>> set(obj, ("a", 0), {})
{'a': [{}]}
>>> set(obj, ("a", 1), {})
{'a': [{}, {}]}
>>> set(obj, ("a", 0, "b"), 1)
{'a': [{'b': 1}, {}]}
>>> set(obj, ("a", -1, "b"), 2)
{'a': [{'b': 1}, {'b': 2}]}
```

This function returns the object with the new `value`.

If the given `path` is a string and `autoparse` is `True`, it is first
converted using the [data_tools.parse] function. Any additional keyword
arguments are passed to the [data_tools.parse] function.

```python
>>> obj = {"a": [{"b": 1}, {"b": 2}]}
>>> set(obj, "a/0/b", 10, sep_chr="/")
{'a': [{'b': 10}, {'b': 2}]}
```

## Function [data\_tools.delete](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L173)
```python
def delete(obj, path, autoparse=AUTOPARSE, **parse_args): ...
```
Delete a value.

Deleting the last value in an object does not delete that object.

```python
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
```

This function returns the object with the deleted value.

If the given `path` is a string and `autoparse` is `True`, it is first
converted using the [data_tools.parse] function. Any additional keyword
arguments are passed to the [data_tools.parse] function.

```python
>>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
>>> delete(obj, "a/0/b/c", sep_chr="/")
{'a': [{'b': {}}, {'b': {'c': 100}}]}
```

## Function [data\_tools.update](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L219)
```python
def update(obj, path, func, autoparse=AUTOPARSE, **parse_args): ...
```
Update a value based on the current value.

This is an efficient alternative to getting a value, modifying it, and
setting it back.

```python
>>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
>>> update(obj, ["a", 0, "b", "c"], lambda x: x + 1)
{'a': [{'b': {'c': 11}}, {'b': {'c': 100}}]}
>>> update(obj, ["a", 1, "b", "c"], lambda x: x + 1)
{'a': [{'b': {'c': 11}}, {'b': {'c': 101}}]}
>>> update(obj, ["a", 2, "b", "c"], lambda x: x + 1)
Traceback (most recent call last):
...
IndexError: list index out of range
```

However, this function does not allow appending a new value in a list-like
object.

```python
>>> obj = {"a": []}
>>> update(obj, ["a", 0], lambda x: {})
Traceback (most recent call last):
...
IndexError: list index out of range
```

This function returns the updated object.

If the given `path` is a string and `autoparse` is `True`, it is first
converted using the [data_tools.parse] function. Any additional keyword
arguments are passed to the [data_tools.parse] function.

```python
>>> obj = {"a": [{"b": {"c": 10}}, {"b": {"c": 100}}]}
>>> update(obj, "a/0/b/c", lambda x: x + 1, sep_chr="/")
{'a': [{'b': {'c': 11}}, {'b': {'c': 100}}]}
```

## Function [data\_tools.flatten](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L281)
```python
def flatten(obj, only_leaves=False): ...
```
Flatten (or [data_tools.unnest]) a nested object.

This function returns all the paths in the tree structure of the object.

```python
>>> list(flatten({'a': 1, 'b': 1}))
[((), {}), (('a',), 1), (('b',), 1)]
>>> list(flatten({'a': {'B': 1}, 'b': {'B': 1}}))
[((), {}), (('a',), {}), (('b',), {}), (('a', 'B'), 1), (('b', 'B'), 1)]
```

By default, it also returns the non-leaf nodes.
This is useful to reconstruct the object using the [data_tools.unflatten]
function.

Set `only_leaves` to `True` to only return the leaves.
This can be used to generate a CSV-like structure.

```python
>>> list(flatten({'a': {'B': 1}, 'b': {'B': 1}}, only_leaves=True))
[(('a', 'B'), 1), (('b', 'B'), 1)]
```

```python
>>> list(flatten({'a': [{'b': 1}, {'b': 2}]}, only_leaves=False))
[((), {}), (('a',), []), (('a', 0), {}), (('a', 1), {}), (('a', 0, 'b'), 1), (('a', 1, 'b'), 2)]
```

## Function [data\_tools.unflatten](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L329)
```python
def unflatten(paths, sort=False): ...
```
Unflatten (or [data_tools.unnest]) a list of paths.

The expected input is a list of paths, as returned by the [data_tools.flatten]
function.

```python
>>> unflatten([((), {}), (('a',), 1), (('b',), 1)])
{'a': 1, 'b': 1}
>>> unflatten([((), {}), (('a',), {}), (('a', 'B'), 1), (('b',), {}), (('b', 'B'), 1)])
{'a': {'B': 1}, 'b': {'B': 1}}
>>> unflatten([((), {}), (('a',), []), (('a', 0), {}), (('a', 0, 'b'), 1), (('a', 1), {}), (('a', 1, 'b'), 2)])
{'a': [{'b': 1}, {'b': 2}]}
```

Internally, this function sets each path in the given order to create the
nested object. This means that the order of the paths matters.

```python
>>> unflatten([(('a', 0, 'b'), 1), (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), ((),{}), (('a'), [])])
Traceback (most recent call last):
...
ValueError: invalid root
```

The first path must be a single element, which will be the root of the object.

```python
>>> unflatten([((), {}), (('a', 0, 'b'), 1) , (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), (('a',), [])])
Traceback (most recent call last):
...
KeyError: 'a'
```

For setting the 0 index at `a`, there must be a list at `a`.
One way to ensure this is to sort the paths by length.
This way, the paths that set the intermediate values are processed first.

```python
>>> unflatten([((), {}), (('a', 0, 'b'), 1) , (('a', 1, 'b'), 2), (('a', 0), {}), (('a', 1), {}), (('a',), [])], sort=True)
{'a': [{'b': 1}, {'b': 2}]}
```

## Function [data\_tools.unnest](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L390)
```python
def unnest(*args, **parse_args): ...
```
Alias for [data_tools.flatten]

## Function [data\_tools.nest](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L397)
```python
def nest(*args, **parse_args): ...
```
Alias for [data_tools.unflatten]

## Function [data\_tools.match](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L404)
```python
def match(path, *patterns, wildcard_obj=WILDCARD_OBJ, autoparse=AUTOPARSE, **parse_args): ...
```
Check for a match at the beginning of a path.

```python
>>> path = ["a", "b", "c"]
>>> match(path, ["a"])
True
>>> match(path, ["a", "b"])
True
>>> match(path, ["a", "b", "c"])
True
>>> match(path, ["a", "b", "c", "d"])
False
```

The patterns can contain a `wildcard_obj`, to match any value.
By default, the `wildcard_obj` is `...`, but it can be changed.

```python
>>> match(path, ["a", ...])
True
>>> match(path, [..., "b"])
True
>>> match(path, ["A", ...])
False
>>> match(path, [..., "B"])
False
```

When multiple patterns are given, it returns `True` if any of them matches.

```python
>>> match(path, ["a"], ["A"])
True
```

If the given `path` or the `patterns` are strings and `autoparse` is `True`,
they will be converted using the [data_tools.parse] function.

```python
>>> match("a.b.c", ["a", "b", "c"])
True
>>> match("a.b.c", ["a", "b", "c"], autoparse=False)
Traceback (most recent call last):
...
TypeError: path must be an iterable of keys or indexes
>>> match(("a", "b", "c"), "a.b.c")
True
>>> match(("a", "b", "c"), "a.b.c", autoparse=False)
Traceback (most recent call last):
...
TypeError: pattern must be an iterable of keys or indexes
```

Any additional `parse_args` will be passed to the [data_tools.parse] function.

```python
>>> match("a/b/c", "a/?", sep_chr="/", wildcard_chr="?")
True
```

## Function [data\_tools.fullmatch](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L468)
```python
def fullmatch(path, *patterns, wildcard_obj=WILDCARD_OBJ, autoparse=AUTOPARSE, **parse_args): ...
```
Check for a match in the whole path.

The semantics are the same as the [data_tools.match] function.

```python
>>> path = ("a", "b", "c")
>>> fullmatch(path, ("a"))
False
>>> fullmatch(path, ("a", "b"))
False
>>> fullmatch(path, ("a", "b", "c"))
True
>>> fullmatch(path, ("a", "b", "c", "d"))
False
```

```python
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
```

```python
>>> fullmatch(path, ("a", ..., ...), ("A", ..., ...))
True
```

```python
>>> fullmatch("a/b/c", "a/?/?", sep_chr="/", wildcard_chr="?")
True
```

## Function [data\_tools.parse](https://github.com/kerrigan29a/py_data_tools/blob/main/data_tools.py#L548)
```python
def parse(path, sep_chr=SEP_CHR, quote_chr=None, wildcard_chr=None, wildcard_obj=WILDCARD_OBJ): ...
```
Parse a path string into a sequence of keys and indices.
The separator is `.` by default, but it can be changed.

```python
>>> parse("")
()
>>> parse("a.b.c")
('a', 'b', 'c')
>>> parse("a/b/c", sep_chr="/")
('a', 'b', 'c')
```

The trailing, leading and consecutive separators are ignored.

```python
>>> parse("a.b.")
('a', 'b')
>>> parse(".a.b")
('a', 'b')
>>> parse("a..b.c")
('a', 'b', 'c')
```

If a `quote_chr` is found, the path is parsed as a string.
The default quote characters are `"` and `'`, but they can be changed.
This is useful for keys that contain the separator.

```python
>>> parse("a.b.c")
('a', 'b', 'c')
>>> parse("'a.b'.c")
('a.b', 'c')
>>> parse('"a.b".c')
('a.b', 'c')
>>> parse("/a.b/.c", quote_chr="/")
('a.b', 'c')
```

The numeric parts are parsed as base 10 integers and the rest as strings.
This can be avoided by quoting the numeric parts.

```python
>>> parse("a.0.b.-1")
('a', 0, 'b', -1)
>>> parse("a.'0'.b.-1")
('a', '0', 'b', -1)
```

If `wildcard_chr` is given, it is replaced by the `wildcard_obj`.
The default `wildcard_obj` is `...`, but it can be changed.
A quoted wildcard is not replaced.

```python
>>> parse("a.*.b", wildcard_chr="*")
('a', Ellipsis, 'b')
>>> parse("a.'*'.b", wildcard_chr="*")
('a', '*', 'b')
```


<!-- references -->
[data_tools]: #module-data_tools "Module data_tools"
[`data_tools`]: #module-data_tools "Module data_tools"
[data_tools.get]: #function-data_tools-get "Function get"
[`data_tools.get`]: #function-data_tools-get "Function get"
[data_tools.set]: #function-data_tools-set "Function set"
[`data_tools.set`]: #function-data_tools-set "Function set"
[data_tools.delete]: #function-data_tools-delete "Function delete"
[`data_tools.delete`]: #function-data_tools-delete "Function delete"
[data_tools.update]: #function-data_tools-update "Function update"
[`data_tools.update`]: #function-data_tools-update "Function update"
[data_tools._traverse]: #function-data_tools-_traverse "Function _traverse"
[`data_tools._traverse`]: #function-data_tools-_traverse "Function _traverse"
[data_tools.flatten]: #function-data_tools-flatten "Function flatten"
[`data_tools.flatten`]: #function-data_tools-flatten "Function flatten"
[data_tools.unflatten]: #function-data_tools-unflatten "Function unflatten"
[`data_tools.unflatten`]: #function-data_tools-unflatten "Function unflatten"
[data_tools.unnest]: #function-data_tools-unnest "Function unnest"
[`data_tools.unnest`]: #function-data_tools-unnest "Function unnest"
[data_tools.nest]: #function-data_tools-nest "Function nest"
[`data_tools.nest`]: #function-data_tools-nest "Function nest"
[data_tools.match]: #function-data_tools-match "Function match"
[`data_tools.match`]: #function-data_tools-match "Function match"
[data_tools.fullmatch]: #function-data_tools-fullmatch "Function fullmatch"
[`data_tools.fullmatch`]: #function-data_tools-fullmatch "Function fullmatch"
[data_tools._match]: #function-data_tools-_match "Function _match"
[`data_tools._match`]: #function-data_tools-_match "Function _match"
[data_tools._try_parse]: #function-data_tools-_try_parse "Function _try_parse"
[`data_tools._try_parse`]: #function-data_tools-_try_parse "Function _try_parse"
[data_tools.parse]: #function-data_tools-parse "Function parse"
[`data_tools.parse`]: #function-data_tools-parse "Function parse"

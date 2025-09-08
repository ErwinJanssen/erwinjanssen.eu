---
title: Understanding `is` vs. `==` in Python
slug: python-is-vs-equal
date: '2025-04-04'
abstract: |-
  Explores the differences between Python's `is` and `==` operators, covering
  object identity vs. value equality. Highlights common pitfalls and best
  practices.
categories:
  - Python
---

## The Essentials

- **Identity vs. equality**:
  - `x is y`: Checks if variables `x` and `y` reference the **same object**.
    This is an identity check, equivalent to `id(x) == id(y)`.
  - `x == y`: Checks if objects `x` and `y` have the **same value**. This is an
    equality check, which translates to `x.__eq__(y)`.
- **Common pitfalls**:
  - Incorrect usage of `is` to compare numbers, strings, or other immutable
    types might resolve to `True` due to optimizations like interning.
  - Do not rely on these optimizations since they are implementation-specific
    (e.g., CPython, PyPy).
- **Best practices**:
  - Use `is` for checking if `something is None` or `something is not None`.
  - Use `==` for all other equality comparisons and implement `__eq__()` in
    custom classes if needed.
  - There are valid use cases for `is`, but only if you are confident about
    what you are doing.

For a more in-depth look at how `is` and `==` work, potential pitfalls, and
best practices, keep reading.

## Introduction

When learning Python after working with languages like C, Java, or JavaScript,
it's natural to assume that logical operators behave similarly. While `&&`,
`||`, and `!` in other languages become `and`, `or`, and `not` in Python, using
`is` for equality checks can lead to subtle bugs depending on the Python
implementation. This post aims to clarify the differences between `is` and
`==`, highlight common pitfalls, and provide best practices to avoid these
issues.

## Fundamentals of `is` and `==`

Let's start with the basics by examining what these operators do and how they
differ.

### Identity (`is`)

The operators `is` and `is not` perform an identity comparison by checking if
two variables point to the same object in memory. As described by the [official
Python documentation][python.org-is]:

> The operators `is` and `is not` test for an object's identity: `x is y` is
> true if and only if `x` and `y` are the same object. An Object's identity is
> determined using the `id()` function. `x is not y` yields the inverse truth
> value.

In other words, `x is y` is the same as evaluating `id(x) == id(y)`. The
behavior of the `is` operator is consistent regardless of the objects being
compared because neither the `is` operator nor the built-in `id()` function can
be overloaded.

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(a is b)  # True, because `b` is an alias of `a`
print(a is c)  # False, because `c` is a different list object
```

### Equality (`==`)

The operators `==` and `!=` compare two objects by their values or contents.
The statement `x == y` translates to `x.__eq__(y)`. Unlike `is`, this operator
can be overloaded, allowing control over how objects are compared. Implementing
`__eq__()` for custom classes can be useful for designing elegant and
convenient APIs. However, the downside of overloading is that this operator
might not behave consistently, as it depends on how the `__eq__()` method is
implemented in a class.

#### Example

```python
class Container:
    def __init__(self, data):
        self.data = data


container = Container("test")
print(container is Container("test"))  # False, a new object is created
print(container == Container("test"))  # False, no `__eq__()` method defined
```

Even though two objects are created with the same attributes, they are not
automatically equal. This can be resolved by adding a custom `__eq__()` method:

```python
class Container:
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.data == other.data


container = Container("test")
print(container is Container("test"))  # False, a new object is created
print(container == Container("test"))  # True, because of custom `__eq__()`.
```

Even though this example is basic, it shows that proper method overloading can
lead to more predictable equality checks.

#### Additional note on `!=`

The statement `x != y` translates to `x.__ne__(y)`, which is mostly an historic
artifact. Since Python 3, `__ne__()` returns `not x == y` by default, but
Python 2 did not have such a relation between `==` and `!=` and `__ne__()` had
to be implemented explicitly. The default Python 3 behavior is usually what you
want, so `__ne__()` is rarely implemented in practice anymore.

## Pitfalls

Using `is` for equality comparisons can produce unexpected results due to
certain optimizations in Python. For example, you might expect `x is 5` to
return `False` even if `x` equals 5, but under some conditions, it might return
`True`. These optimizations are dependent on the Python implementation. The
table below illustrates this with some examples.

| Statement                                         | CPython | PyPy    | RustPython |
| :------------------------------------------------ | :------ | :------ | :--------- |
| `256 is 256`                                      | `True`  | `True`  | `True`     |
| `x = 256; x is 256`                               | `True`  | `True`  | `True`     |
| `257 is 257`                                      | `True`  | `True`  | `True`     |
| `x = 257; x is 257`                               | `False` | `True`  | `True`     |
| `x = "test"; x is "test"`                         | `True`  | `True`  | `True`     |
| `x = "something longer"; x is "something longer"` | `False` | `True`  | `True`     |
| `() is ()`                                        | `True`  | `True`  | `True`     |
| `(1, 2, 3) is (1, 2, 3)`                          | `True`  | `True`  | `False`    |
| `x = (1, 2, 3); x is (1, 2, 3)`                   | `False` | `True`  | `False`    |
| `tuple(range(1, 4)) is tuple(range(1, 4))`        | `False` | `False` | `False`    |

The reason for these results is that Python implementations perform certain
optimizations, such as 'interning', for frequently used immutable values. These
optimizations can cause confusion, since `is` can behave like `==` for certain
values.

Luckily, recent versions of CPython and PyPy will warn against this incorrect
usage of `is` with a `SyntaxWarning`, but only when comparing to literals:

- CPython: `SyntaxWarning: "is" with 'int' literal. Did you mean "=="?`
- PyPy: `SyntaxWarning: "is" with a literal. Did you mean "=="?`

### Reflexivity

In general, if `x is y`, then `x == y` is also `True`. This property is known
as a [reflexive relation][wikipedia-reflexive-relation], and it is the reason
that objects without an `__eq__()` method only compare equal to themselves.
When implementing custom `__eq__()` methods, reflexivity usually follows
naturally. However, it is possible to break reflexivity. Consider the following
example:

```python
class BadEq:
    def __eq__(self, other):
        return False


bad_eq = BadEq()
print(bad_eq is bad_eq)  # True, it is the same instance.
print(bad_eq == bad_eq)  # False, because of the custom __eq__().
```

Python itself makes several assumptions about reflexivity. For example,
a `list` is always equal to itself, regardless of its contents:

```python
class BadEq:
    def __eq__(self, other):
        return False


lst = [bad_eq]
print(lst is lst)  # True, same object
print(lst == lst)  # True, because of reflexivity
print(all(x == x for x in lst))  # False, because of BadEq.__eq__()
```

Custom classes aside, reflexivity holds for all built-in classes and types,
with one notable exception: [NaN][python.org-nan]. The IEEE Standard for
Floating-Point Arithmetic (IEEE 754) dictates that NaN should not be equal to
anything, including itself. For this reason, to check if a variable is NaN, use
`math.isnan()`.

```python
from math import nan, isnan  # or `nan = float("nan")`

print(nan is nan)  # True
print(nan == nan)  # False
print(isnan(nan))  # True
```

## Best practices for using `is` and `==`

Now that we have discussed both operators in more detail, how do we use them
effectively?

### When in doubt, use `==`

Generally speaking, there are not many cases where you would want to compare
the identity of two objects. Most of the time, you want to compare objects
based on their value instead, for which you should use `==`.

Implement `__eq__()` for custom classes to have more meaningful value
comparisons. You can also consider using the standard library module
[`dataclasses`][python.org-dataclasses], which automatically implements
`__eq__()` based on the class's attributes.

### Always use `is` for `None` (and other singletons)

In Python, `None` is guaranteed to be a singleton, all occurrences of `None`
reference the same object. As such, you can use `is` and `is not` to check if
a variable is `None`.

But you might wonder "why the exception if `== None` and `!= None` work as
well? This has multiple reasons:

- The `==` operator can be overloaded. So in theory it is possible to implement
  `__eq__()` is such a way that `x == None` would evaluate to `True` even
  though `x` might not be `None` at all. Using `is` ensures that you are
  checking what you want.
- Using `is` has a small performance benefit over `==` since it does not have
  look up and invoke the correct `__eq__()` for the object being compared.

There are more singletons in Python, the most notable being `True` and `False`.
It is therefore perfectly valid to do `if something is False`. This pattern is
rarely used, and often `if not something` suffices, but it is not the same.
Empty collections, empty strings, and the number 0 are all treated as `False`
in an `if` statement, but they are not identical to `False`:

```python
print(not [])  # True, because `bool([])` returns `False`.
print([] is False)  # False, because these are different objects.
```

Little known fact: there are more builtin singletons in Python, but those are
never really treated as such. Some examples are the elipses `...` and
`NotImplemented`. You can check this for yourself:

```python
print(type(...))  # <class 'ellipsis'>
print(type(...)() is ...)  # True
print(type(NotImplemented)() is NotImplemented)  # True
```

### Use `is` for object caches

Sometimes you truly need to know if two variables point to the same object. One
example is when caching values and wanting to verify that something is indeed
cached.

```python
class ExpensiveObject:
    def __init__(self, value):
        self.value = value


def get_expensive_object(key):
    if cache.get(key) is None:
        cache[key] = ExpensiveObject(key)
    return cache[key]


cache = {}
obj1 = get_expensive_object(42)
obj2 = get_expensive_object(42)

print(obj1 is obj2)  # True, both variables point to the cached object.
```

### Avoid using `is` or `==` for comparing types

Types, especially built-in types, can generally be treated as singletons. As
such, it is possible to use both `is` and `==` to compare them. However, this
is not recommended, and you should use `isinstance()` instead. These are some
examples that illustrate why.

`isinstance()` handles subclasses:

```python
class CustomString(str):
    pass


custom_text = CustomString("some text")

print(type(custom_text) is CustomString)  # True, type is exact match
print(type(custom_text) is str)  # False, subclass is not an exact match
print(isinstance(custom_text, CustomString))  # True
print(isinstance(custom_text, str))  # True, `isinstance` handles subclasses
```

`isinstance()` can check against multiple types:

```python
x = 5
print(type(x) is int or type(x) is float)  # Requires chained `type` and `or`
print(isinstance(x, (int, float))  # Can check against multiple types.
```

There are often 'abstract base classes' available for common patterns, and
these can only be used with `isinstance()`, since no object will have the
abstract base class as its actual type. In this example, using `isinstance`
with `numbers.Number` will match any kind of number type, including the other
built-in number type `complex`.

```python
import numbers

print(isinstance(5, numbers.Number))  # True
print(isinstance(complex(1.0, 1.0), numbers.Number))  # True
```

# Conclusion

While the `is` and `==` operators may appear similar at first glance, they
serve distinct roles and are not interchangeable. Of the two, `==` is used most
often since an object's value is usually what matters. The `is` operator should
be reserved for identity checks only, such as verifying that a variable is
`None` or ensuring that two variables point to the same object.

The pitfalls discussed illustrate how implementation-specific optimizations can
yield unexpected results when these operators are misused. These optimizations
should never be relied upon, but you must be aware of them to avoid subtle
bugs.

All in all, it shows the importance of understanding Python's fundamentals. By
adhering to the best practices, your code will be clearer, more predictable,
and ultimately more maintainable.

[python.org-dataclasses]: https://docs.python.org/3/library/dataclasses.html
[python.org-is]: https://docs.python.org/3/reference/expressions.html#is-not
[python.org-nan]: https://docs.python.org/3/library/math.html#math.nan
[wikipedia-reflexive-relation]: https://en.wikipedia.org/wiki/Reflexive_relation

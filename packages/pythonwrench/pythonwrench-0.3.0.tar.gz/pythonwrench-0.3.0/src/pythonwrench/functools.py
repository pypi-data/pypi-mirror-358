#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec

from pythonwrench._core import _decorator_factory, return_none  # noqa: F401
from pythonwrench.inspect import get_argnames

T = TypeVar("T")
P = ParamSpec("P")
U = TypeVar("U")


class Compose(Generic[T, U]):
    """Compose callables to chain calls sequentially."""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], Any],
        fn4: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(self, *fns: Callable) -> None: ...

    def __init__(self, *fns: Callable) -> None:
        super().__init__()
        self.fns = fns

    def __call__(self, x: T) -> U:
        for fn in self.fns:
            x = fn(x)
        return x  # type: ignore

    def __getitem__(self, idx: int, /) -> Callable[[Any], Any]:
        return self.fns[idx]

    def __len__(self) -> int:
        return len(self.fns)


compose = Compose  # type: ignore


def filter_and_call(fn: Callable[..., T], **kwargs: Any) -> T:
    """Filter kwargs with function arg names and call function."""
    argnames = get_argnames(fn)
    kwargs_filtered = {
        name: value for name, value in kwargs.items() if name in argnames
    }
    return fn(**kwargs_filtered)


def function_alias(alternative: Callable[P, U]) -> Callable[..., Callable[P, U]]:
    """Decorator to wrap function aliases.

    Usage:
    ```
    >>> def f(a: int, b: str) -> str:
    >>>    return a * b

    >>> @function_alias(f)
    >>> def g(*args, **kwargs): ...

    >>> f(2, "a")
    ... "aa"
    >>> g(3, "b")  # calls function f() internally.
    ... "bbb"
    ```
    """
    return _decorator_factory(alternative)


def identity(x: T) -> T:
    """Identity function placeholder."""
    return x

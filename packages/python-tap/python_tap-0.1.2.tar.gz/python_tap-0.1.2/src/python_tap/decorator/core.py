"""Tap decorator."""

from collections.abc import Callable
from functools import partial

from python_tap import store


def wrapper(fn: Callable, *args, **kwargs) -> Callable:  # noqa: ANN002, ANN003
    """Wrap a function."""
    for tapped in store.get():
        tapped(*args, **kwargs, tap_fn=fn)

    return fn(*args, **kwargs)


def tap(fn: Callable) -> Callable:
    """Decorate a function to add the tap feature."""
    return partial(wrapper, fn)

"""Tap store functions."""

from collections.abc import Callable, Generator

_stored_taps: dict[str, Callable | None] = {}


def add(fn: Callable) -> None:
    """Add a tap to the storage."""
    key = fn.__name__

    _stored_taps[key] = fn


def remove(fn: Callable | None = None) -> None:
    """Remove a tap from the storage."""
    if not fn:
        _stored_taps.clear()
    else:
        key = fn.__name__

        _stored_taps.pop(key)


def get() -> Generator[Callable]:
    """Get all stored taps."""
    return (v for v in _stored_taps.values() if v)

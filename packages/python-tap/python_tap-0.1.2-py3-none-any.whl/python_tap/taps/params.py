"""Store function input data."""

import functools
import inspect
from collections.abc import Callable
from typing import Any

_storage: dict = {}


def _collect(fn: Callable, args: Any, kwargs: dict) -> dict:  # noqa: ANN401
    params = inspect.signature(fn).parameters

    data = dict(zip(params, args, strict=False))

    return data | kwargs


def _calculate_namespace(fn: Callable) -> str:
    module = fn.__module__
    name = fn.__qualname__

    return f"{module}.{name}"


def _omit(data: dict, keys: set) -> dict:
    return {k: v for k, v in data.items() if k not in keys}


def _extract_fn(fn: Callable) -> Callable:
    return fn.args[0] if isinstance(fn, functools.partial) else fn


def store(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
    """Store the input data from a function call."""
    key = "tap_fn"

    fn = _extract_fn(kwargs[key])
    ns = _calculate_namespace(fn)
    data = _collect(fn, args, _omit(kwargs, {key}))

    _storage[ns] = data


def get(fn: Callable) -> dict | None:
    """Return the stored input data for a specific function."""
    extracted = _extract_fn(fn)
    ns = _calculate_namespace(extracted)

    return _storage.get(ns)


def get_all() -> dict:
    """Return all stored input data."""
    return _storage

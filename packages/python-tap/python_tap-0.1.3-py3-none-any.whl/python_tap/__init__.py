"""A Python implementation of tap. Useful for REPL Driven Development."""

from python_tap import taps
from python_tap.decorator.core import tap
from python_tap.store.core import add, remove

__all__ = ["add", "remove", "tap", "taps"]

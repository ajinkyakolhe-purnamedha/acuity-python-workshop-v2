"""Reusable decorators — Day 2 Lab 5 (`@retry`, `@log_calls`).

A decorator wraps a function to add behavior without touching its body. You
write two you'll reuse all week — `@retry` makes the API client resilient,
`@log_calls` traces it. `functools.wraps` is given (Day-3 fixtures assert the
wrapped name survives). Fill every `# TODO`.

Concepts: codealong/module-5.ipynb §"Decorators".
"""

from __future__ import annotations

import functools
import logging
import time

logger = logging.getLogger(__name__)


def log_calls(func):
    """Log the function's name on every call, then run it unchanged."""

    @functools.wraps(func)                       # keep func's real __name__
    def wrapper(*args, **kwargs):
        # TODO: logger.info("call %s", func.__name__); then return func(*args, **kwargs)
        ...

    return wrapper


def retry(times: int = 3, delay: float = 0.0, exceptions: tuple = (Exception,)):
    """A decorator *with config*: retry the call, but only on the listed exceptions.

    `retry(times=3)` returns the actual decorator (one extra layer).
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: loop  for attempt in range(1, times + 1):
            #           try: return func(*args, **kwargs)            # success -> done
            #           except exceptions:
            #               if attempt == times: raise               # last try -> give up
            #               time.sleep(delay)                        # else wait and retry
            ...

        return wrapper

    return decorator

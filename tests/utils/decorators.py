from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

import pytest
from scrapy.utils.defer import deferred_from_coro
from scrapy.utils.reactor import is_reactor_installed

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from twisted.internet.defer import Deferred


_P = ParamSpec("_P")


def coroutine_test(
    coro_f: Callable[_P, Awaitable[None]],
) -> Callable[_P, Awaitable[None]]:
    """Mark a test function that returns a coroutine.

    * with ``pytest-twisted`` this converts a coroutine into a
      :class:`twisted.internet.defer.Deferred`
    * with ``pytest-asyncio`` this is a no-op

    In addition to handling asynchronous test functions this can also be used
    to mark "synchronous" test functions (they still need to be made
    ``async def``) that call code that needs a reactor or a running event loop,
    so that ``pytest-asyncio`` starts a loop for them too.
    """

    if not is_reactor_installed():
        return pytest.mark.asyncio(coro_f)

    @wraps(coro_f)
    def f(*coro_args: _P.args, **coro_kwargs: _P.kwargs) -> Deferred[None]:
        return deferred_from_coro(coro_f(*coro_args, **coro_kwargs))

    return f

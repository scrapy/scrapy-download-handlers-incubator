from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.mockserver.http import MockServer

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def mockserver() -> Generator[MockServer]:
    with MockServer() as mockserver:
        yield mockserver

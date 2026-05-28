from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

import pytest

from tests.test_handlers_base import (
    TestHttpBase,
    TestHttpProxyBase,
    TestHttpsBase,
    TestHttpsCustomCiphersBase,
    TestHttpsInvalidDNSIdBase,
    TestHttpsInvalidDNSPatternBase,
    TestHttpsWrongHostnameBase,
    TestHttpWithCrawlerBase,
    TestMitmProxyBase,
    TestRealWebsiteBase,
    TestSimpleHttpsBase,
)
from tests.utils.decorators import coroutine_test

if TYPE_CHECKING:
    from scrapy.core.downloader.handlers import DownloadHandlerProtocol

    from tests.mockserver.http import MockServer


pytest.importorskip("aiohttp")


class AiohttpDownloadHandlerMixin:
    @property
    def download_handler_cls(self) -> type[DownloadHandlerProtocol]:
        from scrapy_download_handlers_incubator import (  # noqa: PLC0415
            AiohttpDownloadHandler,
        )

        return AiohttpDownloadHandler

    @property
    def settings_dict(self) -> dict[str, Any] | None:
        return {
            "DOWNLOAD_HANDLERS": {
                "http": "scrapy_download_handlers_incubator.AiohttpDownloadHandler",
                "https": "scrapy_download_handlers_incubator.AiohttpDownloadHandler",
            }
        }


class TestHttp(AiohttpDownloadHandlerMixin, TestHttpBase):
    handler_supports_bindaddress_meta = False


class TestHttps(AiohttpDownloadHandlerMixin, TestHttpsBase):
    handler_supports_bindaddress_meta = False

    @pytest.mark.skip(reason="TLS verbose logging is not available for short responses")
    @coroutine_test
    async def test_tls_logging(
        self, mockserver: MockServer, caplog: pytest.LogCaptureFixture
    ) -> None:
        pass


class TestSimpleHttps(AiohttpDownloadHandlerMixin, TestSimpleHttpsBase):
    pass


class TestHttpsWrongHostname(AiohttpDownloadHandlerMixin, TestHttpsWrongHostnameBase):
    pass


class TestHttpsInvalidDNSId(AiohttpDownloadHandlerMixin, TestHttpsInvalidDNSIdBase):
    pass


class TestHttpsInvalidDNSPattern(
    AiohttpDownloadHandlerMixin, TestHttpsInvalidDNSPatternBase
):
    pass


class TestHttpsCustomCiphers(AiohttpDownloadHandlerMixin, TestHttpsCustomCiphersBase):
    pass


class TestHttpWithCrawler(AiohttpDownloadHandlerMixin, TestHttpWithCrawlerBase):
    @pytest.mark.skip(reason="response.ip_address is not available for short responses")
    @coroutine_test
    async def test_response_ip_address(self, mockserver: MockServer) -> None:
        pass


class TestHttpsWithCrawler(TestHttpWithCrawler):
    is_secure = True

    @pytest.mark.skip(
        reason="response.certificate is not available for short responses"
    )
    @coroutine_test
    async def test_response_ssl_certificate(self, mockserver: MockServer) -> None:
        pass

    @pytest.mark.skip(reason="response.ip_address is not available for short responses")
    @coroutine_test
    async def test_response_ip_address(self, mockserver: MockServer) -> None:
        pass


class TestHttpProxy(AiohttpDownloadHandlerMixin, TestHttpProxyBase):
    pass


class TestHttpsProxy(AiohttpDownloadHandlerMixin, TestHttpProxyBase):
    is_secure = True

    @property
    def handler_supports_tls_in_tls(self) -> bool:
        return sys.version_info >= (3, 11)


class TestMitmProxy(AiohttpDownloadHandlerMixin, TestMitmProxyBase):
    handler_supports_socks: bool = False

    @property
    def handler_supports_tls_in_tls(self) -> bool:
        return sys.version_info >= (3, 11)


@pytest.mark.requires_internet
class TestRealWebsite(AiohttpDownloadHandlerMixin, TestRealWebsiteBase):
    pass

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapy import signals
from scrapy.exceptions import StopDownload
from scrapy.http import Request
from scrapy.spiders import Spider

if TYPE_CHECKING:
    from tests.mockserver.http import MockServer


class MockServerSpider(Spider):
    def __init__(
        self,
        *args: Any,
        mockserver: MockServer | None = None,
        is_secure: bool = False,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.mockserver = mockserver
        self.is_secure = is_secure


class MetaSpider(MockServerSpider):
    name = "meta"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.meta: dict[str, Any] = {}

    def closed(self, reason):
        self.meta["close_reason"] = reason


class SingleRequestSpider(MetaSpider):
    seed = None
    callback_func = None
    errback_func = None

    async def start(self):
        if isinstance(self.seed, Request):
            yield self.seed.replace(callback=self.parse, errback=self.on_error)
        else:
            yield Request(self.seed, callback=self.parse, errback=self.on_error)

    def parse(self, response):
        self.meta.setdefault("responses", []).append(response)
        if callable(self.callback_func):
            return self.callback_func(response)
        if "next" in response.meta:
            return response.meta["next"]
        return None

    def on_error(self, failure):
        self.meta["failure"] = failure
        if callable(self.errback_func):
            return self.errback_func(failure)
        return None


class BytesReceivedCallbackSpider(MetaSpider):
    full_response_length = 2**18

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.bytes_received, signals.bytes_received)
        return spider

    async def start(self):
        body = b"a" * self.full_response_length
        url = self.mockserver.url("/alpayload", is_secure=self.is_secure)
        yield Request(url, method="POST", body=body, errback=self.errback)

    def parse(self, response):
        self.meta["response"] = response

    def errback(self, failure):
        self.meta["failure"] = failure

    def bytes_received(self, data, request, spider):
        self.meta["bytes_received"] = data
        raise StopDownload(fail=False)


class BytesReceivedErrbackSpider(BytesReceivedCallbackSpider):
    def bytes_received(self, data, request, spider):
        self.meta["bytes_received"] = data
        raise StopDownload(fail=True)


class HeadersReceivedCallbackSpider(MetaSpider):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.headers_received, signals.headers_received)
        return spider

    async def start(self):
        yield Request(
            self.mockserver.url("/status", is_secure=self.is_secure),
            errback=self.errback,
        )

    def parse(self, response):
        self.meta["response"] = response

    def errback(self, failure):
        self.meta["failure"] = failure

    def headers_received(self, headers, body_length, request, spider):
        self.meta["headers_received"] = headers
        raise StopDownload(fail=False)


class HeadersReceivedErrbackSpider(HeadersReceivedCallbackSpider):
    def headers_received(self, headers, body_length, request, spider):
        self.meta["headers_received"] = headers
        raise StopDownload(fail=True)

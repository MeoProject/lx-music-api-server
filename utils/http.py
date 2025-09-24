import zlib
import httpx
import random
import ujson

from .text import *
from .log import createLogger
from server import variable


ua_list = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
]

logger = createLogger("HTTP")


def _prepare_options(options: dict) -> tuple[str, dict]:
    """Prepare method and options for the request."""
    method = options.pop("method", "GET").upper()

    headers = options.setdefault("headers", {})
    if "User-Agent" not in headers:
        headers["User-Agent"] = random.choice(ua_list)

    if method in ("POST", "PUT"):
        if "body" in options:
            options["data"] = options.pop("body")
        if "form" in options:
            options["data"] = ConvertDictToForm(options.pop("form"))
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if isinstance(options.get("data"), dict):
            options["data"] = ujson.dumps(options["data"])

    return method, options


def _log_response_content(content: bytes) -> None:
    """Log the response content if it's text or zlib-compressed text."""
    if content.startswith(b"\x78\x9c") or content.startswith(b"\x78\x01"):
        try:
            decompressed = zlib.decompress(content)
            if IsValidUTF8(decompressed):
                logger.debug(LogPlainText(decompressed.decode("utf-8")))
            else:
                logger.debug("非文本响应体，不记录")
        except Exception:
            logger.debug("非文本响应体，不记录")
    else:
        if IsValidUTF8(content):
            logger.debug(LogPlainText(content.decode("utf-8")))
        else:
            logger.debug("非文本响应体，不记录")


async def HttpRequest(url: str, options: dict = {}) -> httpx.Response:
    if not variable.http_client:
        timeout = httpx.Timeout(10.0, connect=60.0)
        variable.http_client = httpx.AsyncClient(verify=False, timeout=timeout)

    method, options = _prepare_options(options)

    try:
        reqattr = getattr(variable.http_client, method.lower())
    except AttributeError:
        raise AttributeError(f"不支持的类型: {method}")

    try:
        req: httpx.Response = await reqattr(url, **options)
    except Exception as e:
        logger.error(f"URL: {url} 请求时遇到错误: {e}")

    _log_response_content(req.content)

    return req

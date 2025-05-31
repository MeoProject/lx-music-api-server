import re
import zlib
import traceback
import ujson as json
import random
import aiohttp
import requests
from .log import log
from . import utils
from . import variable


def IsvalidUTF8(text) -> bool:
    try:
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        if "\ufffe" in text:
            return False
        try:
            text.encode("utf-8").decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    except:
        logger.error(traceback.format_exc())
        return False


def IsPlainText(text) -> bool:
    pattern = re.compile(r"[^\x00-\x7F]")
    return not bool(pattern.search(text))


def ConvertDictToForm(dic: dict) -> str:
    return "&".join([f"{k}={v}" for k, v in dic.items()])


def LogPlainText(text: str) -> str:
    if text.startswith("{") and text.endswith("}"):
        try:
            text = json.loads(text)
        except:
            pass
    elif text.startswith("<xml") and text.endswith(">"):
        try:
            text = f"xml: {utils.load_xml(text)}"
        except:
            pass
    return text


ua_list = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
]

logger = log("HTTP Request")


def SyncRequest(url: str, options: dict = {}) -> requests.Response:
    if not variable.SyncClient:
        variable.SyncClient = requests.Session()

    try:
        method = str(options["method"]).upper()
        options.pop("method")
    except Exception as e:
        method = "GET"

    if "User-Agent" not in options["headers"]:
        options["headers"]["User-Agent"] = random.choice(ua_list)

    try:
        reqattr = getattr(variable.SyncClient, method.lower())
    except AttributeError:
        raise AttributeError("不支持的方法: " + method)

    logger.debug(f"HTTP Request: {url}\noptions: {options}")

    if (method == "POST") or (method == "PUT"):
        if options.get("body"):
            options["data"] = options["body"]
            options.pop("body")
        if options.get("form"):
            options["data"] = ConvertDictToForm(options["form"])
            options.pop("form")
            options["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
        if isinstance(options["data"], dict):
            options["data"] = json.dumps(options["data"])

    try:
        logger.debug(url)
        req = reqattr(url, **options)
    except Exception as e:
        logger.error(f"请求时遇到错误: {url}, {e}")
        raise

    logger.debug(f"请求 {url} 成功, 状态码: {req.status_code}")

    if req.content.startswith(b"\x78\x9c") or req.content.startswith(b"\x78\x01"):
        try:
            decompressed = zlib.decompress(req.content)
            if IsvalidUTF8(decompressed):
                logger.debug(LogPlainText(decompressed.decode("utf-8")))
            else:
                logger.debug("非文本响应体，不记录")
        except:
            logger.debug("非文本响应体，不记录")
    else:
        if IsvalidUTF8(req.content):
            logger.debug(LogPlainText(req.content.decode("utf-8")))
        else:
            logger.debug("非文本响应体，不记录")

    def _json():
        return json.loads(req.content)

    setattr(req, "json", _json)

    return req


class ClientResponse:
    def __init__(self, status: int, content: bytes, headers: dict):
        self.status = status
        self.content = content
        self.headers = headers
        self.text = content.decode("utf-8", errors="ignore")

    def json(self) -> str | dict | list:
        return json.loads(self.content)


async def ConvertToRequestsResponse(
    aiohttp_response: aiohttp.ClientResponse,
) -> ClientResponse:
    content = await aiohttp_response.content.read()
    status_code = aiohttp_response.status
    headers = dict(aiohttp_response.headers.items())

    return ClientResponse(status_code, content, headers)


async def AsyncRequest(url: str, options: dict = {}) -> ClientResponse:
    if not variable.AsyncClient:
        variable.AsyncClient = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                verify_ssl=False,
            ),
        )

    method = options.pop("method", "GET").upper()

    dict(options.setdefault("headers", {})).setdefault(
        "User-Agent", random.choice(ua_list)
    )

    try:
        reqattr = getattr(variable.AsyncClient, method.lower())
    except AttributeError:
        raise AttributeError(f"不支持的类型: {method}")

    logger.debug(f"HTTP请求开始: {url}\n设置项: {options}")

    if method in ["POST", "PUT"]:
        if "body" in options:
            options["data"] = options.pop("body")
        if "form" in options:
            options["data"] = ConvertDictToForm(options.pop("form"))
            options["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
        if isinstance(options.get("data"), dict):
            options["data"] = json.dumps(options["data"])

    options["headers"] = {k: str(v) for k, v in options["headers"].items()}

    try:
        logger.debug(url)
        req_ = await reqattr(url, **options)
    except Exception as e:
        logger.error(f"请求时遇到错误: {url, {e}}")
        raise

    req = await ConvertToRequestsResponse(req_)

    logger.debug(f"请求 {url} 成功, 状态码: {req_.status}")

    if req.content.startswith((b"\x78\x9c", b"\x78\x01")):
        try:
            decompressed = zlib.decompress(req.content)
            if (IsvalidUTF8(decompressed)) and (decompressed != None):
                logger.debug(LogPlainText(decompressed.decode("utf-8")))
            else:
                logger.debug("返回不是文本，不输出为日志")
        except:
            logger.debug("返回不是文本，不输出为日志")
    else:
        if (IsvalidUTF8(req.content)) and (req.content != None):
            logger.debug(LogPlainText(req.content.decode("utf-8")))
        else:
            logger.debug("返回不是文本，不输出为日志")

    return req


async def GetIPInfo(ip: str) -> dict:
    try:
        if ip == ("127.0.0.1" or "::1"):
            return {"ip": ip, "local": "本地IP"}

        req = await AsyncRequest(
            "https://mips.kugou.com/check/iscn",
            {"method": "GET", "headers": {"X-Forwarded-For": ip}},
        )
        body = req.json()
        if body["errcode"] != 0:
            return {"ip": ip, "local": "获取失败"}
        return {"ip": ip, "local": body["country"]}
    except:
        return {"ip": ip, "local": "获取失败"}

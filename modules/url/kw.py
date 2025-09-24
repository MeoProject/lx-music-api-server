import random
from utils import http as request
from server.config import config
from server.models import UrlResponse
from server.exceptions import getUrlFailed
from crypt.kuwodes import createDecrypt

tools = {
    "qualityMap": {
        "128k": "128kmp3",
        "320k": "320kmp3",
        "flac": "2000kflac",
        "hires": "4000kflac",
    },
    "qualityMapReverse": {
        128: "128k",
        320: "320k",
        2000: "flac",
        4000: "hires",
    },
    "extMap": {
        "128k": "mp3",
        "320k": "mp3",
        "flac": "flac",
        "hires": "flac",
    },
}


async def getUrl(songId: str | int, quality: str) -> UrlResponse:
    source = random.choice(config.read("module.platform.kw.source_list"))

    params = {
        "user": "359307055300426",
        "source": source,
        "type": "convert_url_with_sign",
        "br": tools["qualityMap"][quality],
        "format": tools["extMap"][quality],
        "sig": "0",
        "rid": songId,
        "network": "WIFI",
        "f": "web",
    }

    params = "&".join([f"{k}={v}" for k, v in params.items()])

    target_url = f"https://mobi.kuwo.cn/mobi.s?{params}"

    req = await request.HttpRequest(
        target_url,
        {
            "method": "GET",
            "headers": {"User-Agent": "okhttp/3.10.0"},
        },
    )

    if req.json()["code"] != 200:
        raise getUrlFailed("网络请求错误")

    body = req.json()["data"]

    url = str(body["url"])
    bitrate = int(body["bitrate"])

    if not url:
        raise getUrlFailed("获取URL失败")

    if bitrate not in tools["qualityMapReverse"]:
        raise getUrlFailed("被自动降到了不支持的音质")
    
    url = UrlResponse(
        url=url.split("?")[0],
        quality=tools["qualityMapReverse"][bitrate],
    )

    return url

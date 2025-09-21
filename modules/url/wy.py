import random
import ujson

from models import UrlResponse
from modules.plat.wy import eEncrypt, QMap
from utils.http import HttpRequest
from server.config import config
from server.exceptions import getUrlFailed


async def getUrl(songId: str, quality: str) -> UrlResponse:
    path = "/api/song/enhance/player/url/v1"
    url = "https://interface.music.163.com/eapi/song/enhance/player/url/v1"
    params = {
        "ids": ujson.dumps([songId]),
        "level": QMap["qualityMap"][quality],
        "encodeType": "mp3",
    }

    req = await HttpRequest(
        url,
        {
            "method": "POST",
            "headers": {
                "User-Agent": "NeteaseMusic/9.3.0.250516233250(9003000);Dalvik/2.1.0 (Linux; U; Android 12; ABR-AL80 Build/9b35a01.0)",
                "Cookie": random.choice(config.read("module.wy.users"))["cookie"],
            },
            "form": eEncrypt(path, params),
        },
    )

    body = req.json()

    if not body["data"] or (not body["data"][0]["url"]):
        raise getUrlFailed("失败")

    data = body["data"][0]
    purl = str(data["url"])

    if data["level"] not in QMap["qualityMapReverse"]:
        raise getUrlFailed("未知的音质")

    if data["level"] != QMap["qualityMap"][quality]:
        return {
            "url": purl.split("?")[0],
            "quality": QMap["qualityMapReverse"][data["level"]],
        }

    url = UrlResponse(
        url=purl.split("?")[0],
        quality=QMap["qualityMapReverse"][data["level"]],
    )

    return url

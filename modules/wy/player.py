import random
import ujson as json
from common import request
from common import config
from common import log
from common.exceptions import FailedException
from .sign import eapiEncrypt

logger = log.log("WyMusic")

tools = {
    "qualityMap": {
        "128k": "standard",
        "192k": "higher",
        "320k": "exhigh",
        "flac": "lossless",
        "hires": "hires",
        "atmos": "jyeffect",
        "master": "jymaster",
    },
    "qualityMapReverse": {
        "standard": "128k",
        "higher": "192k",
        "exhigh": "320k",
        "lossless": "flac",
        "hires": "hires",
        "jyeffect": "atmos",
        "jymaster": "master",
    },
}


async def url(songId, quality):
    path = "/api/song/enhance/player/url/v1"
    requestUrl = "https://interface.music.163.com/eapi/song/enhance/player/url/v1"
    requestBody = {
        "ids": json.dumps([songId]),
        "level": tools["qualityMap"][quality],
        "encodeType": "mp3",
    }
    req = await request.AsyncRequest(
        requestUrl,
        {
            "method": "POST",
            "headers": {
                "User-Agent": "NeteaseMusic/9.3.0.250516233250(9003000);Dalvik/2.1.0 (Linux; U; Android 12; ABR-AL80 Build/9b35a01.0)",
                "Cookie": random.choice(config.ReadConfig("module.wy.users"))["cookie"],
            },
            "form": eapiEncrypt(path, json.dumps(requestBody)),
        },
    )
    body = dict(req.json())
    if (
        not body.get("data")
        or (not body.get("data"))
        or (not body.get("data")[0].get("url"))
    ):
        raise FailedException("失败")

    data = body["data"][0]
    purl = str(data["url"])

    if data["level"] not in tools["qualityMapReverse"]:
        raise FailedException("未知的音质")

    if data["level"] != tools["qualityMap"][quality]:
        logger.info(f"网易云音乐_{songId}, {quality} -> {data['level']}")
        return {
            "url": purl.split("?")[0],
            "quality": tools["qualityMapReverse"][data["level"]],
        }

    return {
        "url": purl.split("?")[0],
        "quality": tools["qualityMapReverse"][data["level"]],
    }

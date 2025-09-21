import random
from utils import http as request
from server.config import config
from models import UrlResponse
from server.exceptions import getUrlFailed
from crypt.kuwodes import createDecrypt

tools = {
    "qualityMap": {
        "128k": "128kmp3",
        "192k": "192kogg",
        "320k": "320kmp3",
        "flac": "2000kflac",
        "hires": "4000kflac",
        "atmos": "20201kmflac",
        "atmos_plus": "20501kmflac",
        "master": "20900kmflac",
    },
    "qualityMapReverse": {
        99: "99k",
        100: "100k",
        128: "128k",
        256: "256k",
        320: "320k",
        2000: "flac",
        4000: "hires",
        20201: "atmos",
        20501: "atmos_plus",
        20900: "master",
    },
    "extMap": {
        "128k": "mp3",
        "320k": "mp3",
        "flac": "flac",
        "hires": "flac",
        "atmos": "mflac",
        "atmos_plus": "mflac",
        "master": "mflac",
    },
}


async def getUrl(songId: str | int, quality: str) -> UrlResponse:
    source = random.choice(config.read("module.kw.source_list"))

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
        raise getUrlFailed("失败")

    body = req.json()["data"]

    url = str(body["url"])
    bitrate = int(body["bitrate"])

    if not url:
        raise getUrlFailed("失败")

    if bitrate not in tools["qualityMapReverse"]:
        raise getUrlFailed("失败")

    if body["format"] == "mflac":
        ekey = createDecrypt(req.json()["data"]["ekey"])
    else:
        ekey = ""

    url = UrlResponse(
        url=url.split("?")[0],
        quality=tools["qualityMapReverse"][bitrate],
        ekey=ekey,
    )

    return url

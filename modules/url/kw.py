import random
from utils import http as request
from server.config import config
from server.models import UrlResponse
from server.exceptions import getUrlFailed

tools = {
    "qualityMap": {
        "128k": "128kmp3",
        "320k": "320kmp3",
        "flac": "2000kflac",
        "hires": "4000kflac",
    },
    "qualityMapReverse": {
        48: "128k",
        99: "128k",
        100: "128k",
        128: "128k",
        192: "128k",
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
    try:
        source = random.choice(config.read("modules.platform.kw.source_list"))

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

        target_url = f"http://mobi.kuwo.cn/mobi.s?{params}"

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

        if bitrate > 4000:
            raise getUrlFailed("返回了加密文件")

        quality = (
            tools["qualityMapReverse"].get(bitrate)
            if tools["qualityMapReverse"].get(bitrate)
            else "128k"
        )

        return UrlResponse(
            url=url.split("?")[0],
            quality=quality,
        )
    except Exception as e:
        raise getUrlFailed(e.args)

import ujson

from server.config import config
from .sign import signBody
from utils.http import HttpRequest


async def signRequest(data):
    data = ujson.dumps(data, ensure_ascii=False)
    s = signBody(data)

    return await HttpRequest(
        f"https://u6.y.qq.com/cgi-bin/musics.fcg?sign=" + s,
        {
            "method": "POST",
            "body": data,
        },
    )


Tools = {
    "File": {
        "fileInfo": {
            "128k": {
                "e": ".mp3",
                "h": "M500",
            },
            "320k": {
                "e": ".mp3",
                "h": "M800",
            },
            "flac": {
                "e": ".flac",
                "h": "F000",
            },
            "hires": {
                "e": ".flac",
                "h": "RS01",
            },
            "atmos": {
                "e": ".flac",
                "h": "Q000",
            },
            "atmos_plus": {
                "e": ".flac",
                "h": "Q001",
            },
            "master": {
                "e": ".flac",
                "h": "AI00",
            },
        },
        "qualityMapReverse": {
            "M500": "128k",
            "M800": "320k",
            "F000": "flac",
            "RS01": "hires",
            "Q000": "atmos",
            "Q001": "atmos_plus",
            "AI00": "master",
        },
    },
    "cdnaddr": (
        config.read("module.tx.cdnaddr")
        if config.read("module.tx.cdnaddr")
        else "http://ws.stream.qqmusic.qq.com/"
    ),
}

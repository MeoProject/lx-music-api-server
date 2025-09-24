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
    },
    "EncryptFile": {
        "fileInfo": {
            "128k": {
                "e": ".mgg",
                "h": "O6M0",
            },
            "320k": {
                "e": ".mgg",
                "h": "O8M0",
            },
            "flac": {
                "e": ".mflac",
                "h": "F0M0",
            },
            "hires": {
                "e": ".mflac",
                "h": "RSM1",
            },
            "atmos": {
                "e": ".mflac",
                "h": "Q0M0",
            },
            "atmos_plus": {
                "e": ".mflac",
                "h": "Q0M1",
            },
            "master": {
                "e": ".mflac",
                "h": "AIM0",
            },
        },
    },
    "cdnaddr": (
        config.read("module.platform.tx.cdnaddr")
        if config.read("module.platform.tx.cdnaddr")
        else "http://ws.stream.qqmusic.qq.com/"
    ),
}

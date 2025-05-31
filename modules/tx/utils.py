from common import request
from common import utils
from common import config
from .sign import sign
import ujson as json

createObject = utils.CreateObject

tools = {
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
    "encryptFile": {
        "fileInfo": {
            "128k": {
                "e": ".mgg",
                "h": "O4M0",
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
        "qualityMapReverse": {
            "O4M0": "128k",
            "O8M0": "320k",
            "F0M0": "flac",
            "RSM1": "hires",
            "Q0M0": "atmos",
            "Q0M1": "atmos_plus",
            "AIM0": "master",
        },
    },
    "cdnaddr": (
        config.ReadConfig("module.tx.cdnaddr")
        if config.ReadConfig("module.tx.cdnaddr")
        else "http://ws.stream.qqmusic.qq.com/"
    ),
}


async def signRequest(data):
    data = json.dumps(data, ensure_ascii=False)
    s = sign(data)

    return await request.AsyncRequest(
        f"https://u.y.qq.com/cgi-bin/musics.fcg?sign=" + s,
        {
            "method": "POST",
            "body": data,
        },
    )


def formatSinger(singerList):
    n = []
    for s in singerList:
        n.append(s["name"])
    return "、".join(n)

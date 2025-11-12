import random
from server.config import config
from server.models import UrlResponse
from server.exceptions import getUrlFailed
from modules.plat.tx import build_comm
from modules.info.tx import getMusicInfo
from modules.plat.tx.utils import signRequest
from modules.constants import translateStrOrInt
from urllib.parse import urlparse

guidList = [
    "Feixiao",
    "Tingyun",
    "Yingxing",
    "History",
    "Chinese",
    "English",
    "Geography",
]

qualityMap = {
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
}
encryptMap = {
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
}


def buildUrl(purl: str, guid: str, vkey: str) -> str:
    params = dict()
    x = urlparse(purl).query.split("&")
    for i in x:
        a, b = i.split("=")
        params[a] = b

    params["guid"] = guid
    params["vkey"] = vkey
    params.pop("redirect")

    cdnaddr = random.choice(config.read("modules.platform.tx.cdns"))
    filename = urlparse(purl).path
    purl = "{cdnaddr}{filename}?{params}".format(
        cdnaddr=cdnaddr,
        filename=filename,
        params="&".join([f"{k}={v}" for k, v in params.items()]),
    )

    return purl


async def getUrl(songId: str | int, quality: str) -> UrlResponse:
    try:
        try:
            info = await getMusicInfo(songId)
        except Exception:
            raise getUrlFailed("详情获取失败")

        songId = info.songMid
        strMediaMid = info.mediaMid

        user_info = config.read("modules.platform.tx.users")
        if quality not in ["128k", "320k", "flac", "hires"]:
            user_info = random.choice(
                [user for user in user_info if user.get("vipType") == "svip"]
            )
        else:
            user_info = random.choice(user_info)

        comm = await build_comm(user_info)
        guid = random.choice(guidList)
        resp = await signRequest(
            {
                "comm": comm,
                "request": {
                    "module": "music.vkey.GetVkey",
                    "method": "UrlGetVkey",
                    "param": {
                        "guid": guid,
                        "uin": user_info["uin"],
                        "downloadfrom": 1,
                        "ctx": 1,
                        "referer": "y.qq.com",
                        "scene": 0,
                        "songtype": [1],
                        "songmid": [songId],
                        "filename": [
                            f"{qualityMap[quality]['h']}{strMediaMid}{qualityMap[quality]['e']}"
                        ],
                    },
                },
            }
        )

        body = resp.json()
        data = body["request"]["data"]["midurlinfo"][0]

        purl = str(data["purl"])
        if not purl:
            raise getUrlFailed(translateStrOrInt(body["request"]["code"]))

        url = buildUrl(purl, guid, data["vkey"])

        return UrlResponse(
            url=url,
            quality=quality,
        )
    except Exception as e:
        raise getUrlFailed(e)

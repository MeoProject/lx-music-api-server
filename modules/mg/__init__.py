import random
import time
from common import request
from common import config
from common import log
from common.exceptions import FailedException

tools = {
    "qualityMap": {"128k": "PQ", "320k": "HQ", "flac": "SQ", "hires": "ZQ"},
    "qualityMapReverse": {"PQ": "128k", "HQ": "320k", "SQ": "flac", "ZQ": "hires"},
}

logger = log.log("MiguMusic")


async def IdGetInfo(songId):
    req = await request.AsyncRequest(
        f"https://c.musicapp.migu.cn/MIGUM3.0/resource/song/by-contentids/v2.0?contentId={songId}",
        {"method": "GET"},
    )
    response = dict(req.json())
    if response.get("code") != "000000":
        raise FailedException("歌曲信息获取失败")
    return response


async def copyrightIdGetInfo(songId):
    req = await request.AsyncRequest(
        f"http://app.c.nf.migu.cn/MIGUM2.0/v1.0/content/resourceinfo.do?resourceType=2&copyrightId={songId}",
        {"method": "GET"},
    )
    response = dict(req.json())
    if response.get("code") != "000000":
        raise FailedException("歌曲信息获取失败")
    return response


def formatSinger(singerList):
    n = []
    for s in singerList:
        n.append(s["name"])
    return "、".join(n)


async def url(songId: str, quality: str):
    _songId = None
    _albumId = None

    try:
        req = await IdGetInfo(songId)
        resourceList = req.get("data", [{}])
        infobody = resourceList[0]
        _name = infobody["songName"]
        _album = infobody["album"]
        _artist = formatSinger(infobody["singerList"])
        _contentId = infobody["contentId"]
        _songId = infobody["songId"]
        _albumId = infobody["albumId"]
    except:
        req = await copyrightIdGetInfo(songId)
        resourceList = req.get("resource", [{}])
        infobody = resourceList[0]
        _name = infobody["songName"]
        _album = infobody["album"]
        _artist = infobody["singer"]
        _contentId = infobody["contentId"]
        _songId = infobody["songId"]
        _albumId = infobody["albumId"]

    user_info = random.choice(config.ReadConfig("module.mg.users"))

    req = await request.AsyncRequest(
        f'https://app.c.nf.migu.cn/MIGUM2.0/strategy/listen-url/v2.4?albumId={_albumId}&lowerQualityContentId={_contentId}&netType=01&resourceType=2&songId={_songId}&toneFlag={tools["qualityMap"][quality]}',
        {
            "method": "GET",
            "headers": {
                "channel": user_info["channel"],
                "token": user_info["token"],
                "ce": user_info["ce"],
                "timestamp": int(round(time.time() * 1000)),
            },
        },
    )

    body = dict(req.json())
    data = dict(body.get("data", {}))

    if not data.get("url"):
        raise FailedException(
            "获取失败: "
            + str(
                dict(data.get("dialogInfo", {})).get("text", "未返回任何数据")
            ).replace("正在播放试听片段。", "")
        )

    data = body["data"]
    purl = str(data["url"])

    play_url = (
        purl.split("?")[0]
        if purl.split("?")[0].startswith("http")
        else "http:" + purl.split("?")[0]
    )

    return {
        "name": _name,
        "artist": _artist,
        "album": _album,
        "url": play_url,
        "quality": tools["qualityMapReverse"].get(data["audioFormatType"], "unknown"),
    }

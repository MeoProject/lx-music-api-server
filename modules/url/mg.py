import time
import random
from server.config import config
from modules.lyric.mg import MrcTools
from utils.http import HttpRequest
from models import Song, UrlResponse
from modules.info.mg import getMusicInfo
from server.exceptions import getUrlFailed

tools = {
    "qualityMap": {"128k": "PQ", "320k": "HQ", "flac": "SQ", "hires": "ZQ"},
    "qualityMapReverse": {"PQ": "128k", "HQ": "320k", "SQ": "flac", "ZQ": "hires"},
}


async def getUrl(songId: str, quality: str) -> Song:
    try:
        info = await getMusicInfo(songId)
    except:
        raise getUrlFailed("详情获取失败")

    user_info = random.choice(config.read("module.mg.users"))

    req = await HttpRequest(
        f'https://app.c.nf.migu.cn/MIGUM2.0/strategy/listen-url/v2.4?albumId={info.albumId}&lowerQualityContentId={info.contentId}&netType=01&resourceType=2&songId={info.songId}&toneFlag={tools["qualityMap"][quality]}',
        {
            "method": "GET",
            "headers": {
                "channel": user_info["channel"],
                "token": user_info["token"],
                "ce": user_info["ce"],
                "timestamp": str(int(round(time.time() * 1000))),
            },
        },
    )

    body = req.json()
    data = body.get("data", {})

    if not data.get("url"):
        raise getUrlFailed(
            "获取失败: "
            + str(data.get("dialogInfo", {}).get("text", "未返回任何数据")).replace(
                "正在播放试听片段。", ""
            )
        )

    data = body["data"]
    purl = str(data["url"])
    play_url = (
        purl.split("?")[0]
        if purl.split("?")[0].startswith("http")
        else "http:" + purl.split("?")[0]
    )
    url = UrlResponse(
        url=play_url,
        quality=tools["qualityMapReverse"][data["audioFormatType"]],
    )

    parser = MrcTools()
    info.lyric = await parser.get_lyric(data)

    song = data["song"]
    if song.get("img1"):
        info.coverUrl = song.get("img1")
    elif song.get("img2"):
        info.coverUrl = song.get("img3")
    elif song.get("img3"):
        info.coverUrl = song.get("img3")
    else:
        info.coverUrl = None

    return Song(info, url)

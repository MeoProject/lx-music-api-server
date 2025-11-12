from utils import orjson
from modules.lyric.wy import getLyric
from modules.plat.wy import eEncrypt
from server.models import SongInfo
from utils.http import HttpRequest
from server.exceptions import getSongInfoFailed
from modules.plat import formatPlayTime, formatSinger


async def getMusicInfo(songId: str):
    path = "/api/v3/song/detail"
    url = "http://interface.music.163.com/eapi/v3/song/detail"
    params = {
        "c": [orjson.dumps({"id": songId})],
        "ids": [songId],
    }
    infoRequest = await HttpRequest(
        url,
        {
            "method": "POST",
            "form": eEncrypt(path, params),
        },
    )

    infoBody = infoRequest.json()

    if infoBody["code"] != 200:
        raise getSongInfoFailed("获取音乐信息失败")

    info = infoBody["songs"][0]

    try:
        lyric = await getLyric(songId)
    except:
        lyric = None

    return SongInfo(
        songId=info.get("id"),
        songName=info.get("name"),
        artistName=formatSinger(info.get("ar", [])),
        albumName=info.get("al", {}).get("name"),
        albumId=info.get("al", {}).get("id"),
        duration=(
            formatPlayTime(info.get("dt", 0) / 1000)
            if info.get("dt") is not None
            else None
        ),
        coverUrl=info.get("al", {}).get("picUrl"),
        lyric=lyric,
    )

from server.models import SongInfo
from utils.http import HttpRequest
from modules.plat import formatSinger
from server.exceptions import getSongInfoFailed


async def IdGetInfo(songId: int | str):
    req = await HttpRequest(
        f"http://c.musicapp.migu.cn/MIGUM3.0/resource/song/by-contentids/v2.0?contentId={songId}",
        {"method": "GET"},
    )

    response = req.json()

    if (response.get("code") != "000000") or (len(response["data"]) == 0):
        raise getSongInfoFailed("歌曲信息获取失败")

    resourceList = response.get("data", [{}])
    infobody = resourceList[0]

    return SongInfo(
        songId=infobody.get("songId"),
        songName=infobody.get("songName"),
        artistName=formatSinger(infobody.get("singerList", [])),
        albumName=infobody.get("album"),
        albumId=infobody.get("albumId"),
        contentId=infobody.get("contentId"),
    )


async def copyrightIdGetInfo(songId):
    req = await HttpRequest(
        f"http://app.c.nf.migu.cn/MIGUM2.0/v1.0/content/resourceinfo.do?resourceType=2&copyrightId={songId}",
        {"method": "GET"},
    )
    response = req.json()

    if (response.get("code") != "000000") or (len(response["resource"]) == 0):
        raise getSongInfoFailed("歌曲信息获取失败")

    resourceList = response.get("resource", [{}])
    infobody = resourceList[0]

    return SongInfo(
        songId=infobody.get("songId"),
        songName=infobody.get("songName"),
        artistName=infobody.get("singer"),
        albumName=infobody.get("album"),
        albumId=infobody.get("albumId"),
        contentId=infobody.get("contentId"),
    )


async def getMusicInfo(songId: int | str):
    try:
        return await IdGetInfo(songId)
    except:
        return await copyrightIdGetInfo(songId)

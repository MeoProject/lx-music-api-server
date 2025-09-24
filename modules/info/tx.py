from modules.plat.tx.utils import signRequest
from modules.plat.tx import build_common_params
from server.models import SongInfo
from server.exceptions import getSongInfoFailed
from modules.plat import formatPlayTime, formatSinger
from modules.lyric.tx import getLyric


async def IdGetInfo(songid: int) -> SongInfo:
    commonParams = await build_common_params()
    infoReqBody = {
        "comm": commonParams,
        "req": {
            "module": "music.trackInfo.UniformRuleCtrl",
            "method": "CgiGetTrackInfo",
            "param": {"types": [1], "ids": [songid], "ctx": 0},
        },
    }
    infoRequest = await signRequest(infoReqBody)
    infoBody = infoRequest.json()

    if infoBody["code"] != 0 or infoBody["req"]["code"] != 0:
        raise getSongInfoFailed("获取音乐信息失败")

    info = infoBody["req"]["data"]["tracks"][0]

    try:
        lyric = await getLyric(info["id"])
    except:
        lyric = None

    return SongInfo(
        songId=info.get("id"),
        songMid=info.get("mid"),
        songName=(info.get("title", "") + info.get("subtitle", "")),
        artistName=formatSinger(info.get("singer", [])),
        albumName=(
            info.get("album", {}).get("title", "")
            + info.get("album", {}).get("subtitle", "")
        ),
        albumId=info.get("album", {}).get("id"),
        albumMid=info.get("album", {}).get("mid"),
        duration=(
            formatPlayTime(info.get("interval"))
            if info.get("interval") is not None
            else None
        ),
        mediaMid=info.get("file", {}).get("media_mid"),
        lyric=lyric,
    )


async def MidGetInfo(mid: str) -> SongInfo:
    commonParams = await build_common_params()
    infoReqBody = {
        "comm": commonParams,
        "req": {
            "method": "get_song_detail_yqq",
            "param": {"song_type": 0, "song_mid": mid},
            "module": "music.pf_song_detail_svr",
        },
    }
    infoRequest = await signRequest(infoReqBody)
    infoBody = infoRequest.json()

    if infoBody["code"] != 0 or infoBody["req"]["code"] != 0:
        raise getSongInfoFailed("获取音乐信息失败")

    info = infoBody["req"]["data"]["track_info"]

    try:
        lyric = await getLyric(info["id"])
    except:
        lyric = None

    return SongInfo(
        songId=info.get("id"),
        songMid=info.get("mid"),
        songName=(info.get("title", "") + info.get("subtitle", "")),
        artistName=formatSinger(info.get("singer", [])),
        albumName=(
            info.get("album", {}).get("title", "")
            + info.get("album", {}).get("subtitle", "")
        ),
        albumId=info.get("album", {}).get("id"),
        albumMid=info.get("album", {}).get("mid"),
        duration=(
            formatPlayTime(info.get("interval"))
            if info.get("interval") is not None
            else None
        ),
        mediaMid=info.get("file", {}).get("media_mid"),
        lyric=lyric,
    )


async def getMusicInfo(songId: int | str):
    if songId.isdigit() or isinstance(songId, int):
        return await IdGetInfo(int(songId))
    elif isinstance(songId, str):
        return await MidGetInfo(songId)

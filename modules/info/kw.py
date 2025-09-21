from utils import http as request
from models import SongInfo
from modules.lyric.kw import getLyric
from modules.plat import formatPlayTime
from server.exceptions import getSongInfoFailed


async def GetPic(songId: str | int, albumId: str | int) -> str:
    pic_url_req = await request.HttpRequest(
        f"http://artistpicserver.kuwo.cn/pic.web?corp=kuwo&type=rid_pic&pictype=500&size=500&rid={songId}"
    )
    picUrl = pic_url_req.text

    if picUrl == "NO_PIC":
        pic_url_req = await request.HttpRequest(
            f"https://searchlist.kuwo.cn/r.s?stype=albuminfo&albumid={albumId}&show_copyright_off=1&alflac=1&vipver=1&sortby=1&newver=1&mobi=1"
        )
        picUrl = pic_url_req.json().get("hts_img", "")

    return picUrl


async def getMusicInfo(songId: str | int) -> SongInfo:
    url = f"http://musicpay.kuwo.cn/music.pay?ver=MUSIC_9.1.1.2_BCS2&src=mbox&op=query&signver=new&action=play&ids={songId}&accttype=1&appuid=38668888"
    req = await request.HttpRequest(url)

    if req.status_code != 200:
        raise getSongInfoFailed(f"获取歌曲信息失败: {req.json()}")

    body = req.json()["songs"][0]
    pic = await GetPic(body["id"], body["albumid"])

    try:
        lrc = await getLyric(songId)
    except:
        lrc = None

    return SongInfo(
        songId=body.get("id"),
        songName=body.get("name"),
        artistName=body.get("artist"),
        albumName=body.get("album"),
        albumId=body.get("albumid"),
        duration=(
            formatPlayTime(body.get("duration"))
            if body.get("duration") is not None
            else None
        ),
        coverUrl=pic,
        lyric=lrc,
    )

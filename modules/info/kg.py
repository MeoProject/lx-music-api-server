import time
from server.models import SongInfo
from utils import http as request
from server.exceptions import getSongInfoFailed


async def getMusicInfo(hash_):
    tn = int(time.time())
    url = "http://gateway.kugou.com/v3/album_audio/audio"
    options = {
        "method": "POST",
        "headers": {
            "KG-THash": "13a3164",
            "KG-RC": "1",
            "KG-Fake": "0",
            "KG-RF": "00869891",
            "User-Agent": "Android712-AndroidPhone-11451-376-0-FeeCacheUpdate-wifi",
            "x-router": "kmr.service.kugou.com",
        },
        "body": {
            "area_code": "1",
            "show_privilege": "1",
            "show_album_info": "1",
            "is_publish": "",
            "appid": 1005,
            "clientver": 11451,
            "mid": "114514",
            "dfid": "-",
            "clienttime": tn,
            "key": "OIlwlieks28dk2k092lksi2UIkp",
            "data": [{"hash": hash_}],
        },
    }
    body = await request.HttpRequest(url, dict(options))
    body = body.json()
    data = body["data"][0][0] if (body["data"] and body["data"][0]) else None
    if not data:
        raise getSongInfoFailed()
    return (
        SongInfo(
            songId=data.get("audio_id"),
            songName=data.get("ori_audio_name"),
            artistName=data.get("author_name"),
            albumName=data.get("album_info", {}).get("album_name"),
            hash=data.get("audio_info", {}).get("hash"),
            albumId=data.get("album_info", {}).get("album_id"),
            albumAudioId=data.get("album_audio_id"),
            duration=(
                int(int(data.get("audio_info", {}).get("timelength", 0)) / 1000)
                if data.get("audio_info", {}).get("timelength")
                else None
            ),
            coverUrl=(
                str(data.get("album_info", {}).get("sizable_cover", "")).format(
                    size="500"
                )
                if data.get("album_info", {}).get("sizable_cover")
                else None
            ),
        ),
        data,
    )

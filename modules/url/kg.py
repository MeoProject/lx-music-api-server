import time
import random
from models import UrlResponse
from server.config import config
from server.exceptions import getUrlFailed
from modules.info.kg import getMusicInfo
from modules.plat.kg.utils import tools, getKey, signRequest


async def getUrl(songId: str, quality: str) -> dict:
    try:
        songId = songId.lower()
        info, info_body = await getMusicInfo(songId)
        thash = info_body["audio_info"][tools["qualityHashMap"][quality]]
        album_id = info.albumId
        album_audio_id = info.albumAudioId

        if not thash:
            raise getUrlFailed("获取歌曲信息失败或没有该音质资源")
    except Exception as e:
        raise getUrlFailed(f"获取音乐信息失败: {e}")

    try:
        user_info = random.choice(config.read("module.kg.users"))

        params = {
            "album_id": album_id,
            "userid": user_info["userid"],
            "area_code": 1,
            "hash": thash.lower(),
            "mid": tools["mid"],
            "appid": tools["app"]["appid"],
            "ssa_flag": "is_fromtrack",
            "clientver": tools["app"]["clientver"],
            "token": user_info["token"],
            "album_audio_id": album_audio_id,
            "behavior": "play",
            "clienttime": int(time.time()),
            "pid": tools["app"]["pid"],
            "key": getKey(thash, user_info),
            "quality": tools["qualityMap"][quality],
            "version": tools["app"]["clientver"],
            "dfid": "-",
            "pidversion": 3001,
        }

        headers = {
            "User-Agent": "Android12-AndroidCar-20089-46-0-NetMusic-wifi",
            "KG-THash": "255d751",
            "KG-Rec": "1",
            "KG-RC": "1",
        }

        req = await signRequest(
            "https://tracker.kugou.com/v5/url",
            params,
            {"headers": headers},
        )
        body = dict(req.json())

        if not body["url"]:
            match body["status"]:
                case 3:
                    return getUrlFailed("酷狗无版权的歌曲，目前无解")
                case 2:
                    raise getUrlFailed("链接获取失败，可能出现验证码或数字专辑未购买")
                case 1:
                    raise getUrlFailed("链接获取失败, 可能是数字专辑或者API失效")
                case _:
                    raise getUrlFailed("未知错误导致获取链接失败")

        play_url = body["url"][0]
        url = UrlResponse(play_url, quality)

        return url
    except Exception as e:
        raise getUrlFailed(f"未知错误: {e}")

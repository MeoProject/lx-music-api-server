import time
import random
from common import config
from common.exceptions import FailedException
from .utils import tools, getKey, signRequest
from .musicInfo import getMusicInfo


async def url(songId: str, quality: str) -> dict:
    try:
        songId = songId.lower()
        info_body = await getMusicInfo(songId)
        thash = info_body["audio_info"][tools["qualityHashMap"][quality]]
        album_id = (
            info_body["album_info"]["album_id"]
            if (info_body.get("album_info") and info_body["album_info"].get("album_id"))
            else None
        )
        album_audio_id = info_body["album_audio_id"]

        if not thash:
            raise FailedException("获取歌曲信息失败或没有该音质资源")
    except Exception as e:
        raise FailedException(f"获取音乐信息失败: {e}")

    try:
        user_info = random.choice(config.ReadConfig("module.kg.users"))

        params = {
            "album_id": album_id,
            "userid": user_info["userid"],
            "area_code": 1,
            "hash": thash.lower(),
            "mid": tools["mid"],
            "appid": tools[user_info["version"]]["appid"],
            "ssa_flag": "is_fromtrack",
            "clientver": tools[user_info["version"]]["clientver"],
            "token": user_info["token"],
            "album_audio_id": album_audio_id,
            "behavior": "play",
            "clienttime": int(time.time()),
            "pid": tools[user_info["version"]]["pid"],
            "key": getKey(thash, user_info),
            "quality": tools["qualityMap"][quality],
            "version": tools[user_info["version"]]["clientver"],
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
            version=user_info["version"],
        )
        body = dict(req.json())

        if not body["url"]:
            match body["status"]:
                case 3:
                    return FailedException("酷狗无版权的歌曲，目前无解")
                case 2:
                    raise FailedException(
                        "链接获取失败，可能出现验证码或数字专辑未购买"
                    )
                case 1:
                    raise FailedException("链接获取失败, 可能是数字专辑或者API失效")
                case _:
                    raise FailedException("未知错误导致获取链接失败")

        play_url = body["url"][0]

        return {
            "url": play_url,
            "quality": quality,
        }

    except Exception as e:
        raise FailedException(f"未知错误: {e}")

from common.exceptions import FailedException
from .utils import signRequest


async def getMusicInfo(songid: str | int):
    if songid.isdigit():
        infoReqBody = {
            "comm": {"ct": "19", "cv": "1859", "uin": "0"},
            "req": {
                "module": "music.trackInfo.UniformRuleCtrl",
                "method": "CgiGetTrackInfo",
                "param": {"types": [1], "ids": [songid], "ctx": 0},
            },
        }
    else:
        infoReqBody = {
            "comm": {
                "ct": "19",
                "cv": "1859",
                "uin": "0",
            },
            "req": {
                "module": "music.pf_song_detail_svr",
                "method": "get_song_detail_yqq",
                "param": {
                    "song_type": 0,
                    "song_mid": songid,
                },
            },
        }
    infoRequest = await signRequest(infoReqBody)
    infoBody = infoRequest.json()
    if infoBody["code"] != 0 or infoBody["req"]["code"] != 0:
        raise FailedException("获取音乐信息失败")
    return infoBody["req"]["data"]

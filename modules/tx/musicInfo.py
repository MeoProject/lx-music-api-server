# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: musicInfo.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from .utils import signRequest


async def getMusicInfo(songid):
    infoReqBody = {
        "comm": {
            "ct": '19',
            "cv": '1859',
            "uin": '0',
        },
        "req": {
            "module": 'music.pf_song_detail_svr',
            "method": 'get_song_detail_yqq',
            "param": {
                "song_type": 0,
                "song_mid": songid,
            },
        },
    }
    infoRequest = await signRequest(infoReqBody, True)
    infoBody = infoRequest.json()
    if (infoBody['code'] != 0 or infoBody['req']['code'] != 0):
        raise FailedException("获取音乐信息失败")
    return infoBody['req']['data']
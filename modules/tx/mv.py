# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: mv.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import asyncio
import json
from .utils import signRequest


async def getMvPlayURLandInfo(vid):
    info = signRequest({
        "comm": {"ct": 24, "cv": 4747474},
        "mvinfo": {
            "module": "video.VideoDataServer",
            "method": "get_video_info_batch",
            "param": {
                "vidlist": [vid],
                "required": [
                    "vid",
                    "type",
                    "sid",
                    "cover_pic",
                    "duration",
                    "singers",
                    "video_switch",
                    "msg",
                    "name",
                    "desc",
                    "playcnt",
                    "pubdate",
                    "isfav",
                    "gmid",
                    "songmid"
                ],
            },
        },
    }, True)
    urlreq = signRequest({
        "comm": {
            "ct": 24,
            "cv": 4747474,
            "g_tk": 812935580,
            "uin": 0,
            "format": "json",
            "platform": "yqq"
        },
        "mvUrl": {
            "module": "gosrf.Stream.MvUrlProxy",
            "method": "GetMvUrls",
            "param": {
                "vids": [vid],
                "request_typet": 10001,
                "addrtype": 3,
                "format": 264
            }
        }
    })
    res = await asyncio.gather(info, urlreq)
    i = res[0]
    # output i with formatted json
    print(json.dumps(i.json(), indent=2, ensure_ascii = False))
    url = res[1]
    file_info = {}
    urlbody = url.json()
    if (urlbody['code'] == 0 and urlbody['mvUrl']['code'] == 0):
        for u in url['mvUrl']['data'][vid]['mp4']:
            if (u['filetype'] == 0):
                if (u['fileSize']):
                    pass
                pass
            pass
        pass
    pass



# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import random
from common import Httpx
from common import config
from common import variable
from common.exceptions import FailedException
from . import refresh_login

tools = {
    'qualityMap': {
        '128k': '1',
        '320k': '2',
        'flac': '3',
        'flac24bit': '4',
        "master": "5"
    },
    'qualityMapReverse': {
        '000009': '128k',
        '020010': '320k',
        '011002': 'flac',
        '011005': 'flac24bit',
    },
}

async def url(songmid, quality):
    info_url = f"http://app.c.nf.migu.cn/MIGUM2.0/v1.0/content/resourceinfo.do?resourceType=2&copyrightId=" + songmid
    info_request = await Httpx.AsyncRequest(info_url, {"method": "POST", "cache": 259200})
    infobody = info_request.json()
    if infobody["code"] != "000000":
        raise FailedException("failed to fetch song info")
    user_info = config.read_config('module.mg.user') if (not variable.use_cookie_pool) else random.choice(config.read_config('module.cookiepool.mg'))
    req = await Httpx.AsyncRequest(f'https://m.music.migu.cn/migumusic/h5/play/auth/getSongPlayInfo?type={tools["qualityMap"][quality]}&copyrightId={infobody["resource"][0]["copyrightId"]}', {
        'method': 'GET',
        'headers': {
            'User-Agent': user_info['useragent'],
            "by": user_info["by"],
            "Cookie": "SESSION=" + user_info["session"],
            "Referer": "https://m.music.migu.cn/v4/",
            "Origin": "https://m.music.migu.cn",
        },
    })
    try:
        body = req.json()

        if (int(body['code']) != 200 or (not body.get("data")) or (not body["data"]["playUrl"])):
            raise FailedException(body.get("msg") if body.get("msg") else "failed")

        data = body["data"]

        return {
            'url': body["data"]["playUrl"].split("?")[0] if body["data"]["playUrl"].split("?")[0].startswith("http") else "http:" + body["data"]["playUrl"].split("?")[0],
            'quality': tools['qualityMapReverse'].get(data['formatId']) if (tools['qualityMapReverse'].get(data['formatId'])) else "unknown",
        }
    except:
        raise FailedException('failed')
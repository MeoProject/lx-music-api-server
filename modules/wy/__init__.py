# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from common import config
from common.exceptions import FailedException
from .encrypt import eapiEncrypt
import ujson as json

tools = {
    'qualityMap': {
        '128k': 'standard',
        '320k': 'exhigh',
        'flac': 'lossless',
        'flac24bit': 'hires',
        "dolby": "jyeffect",
        "sky": "jysky",
        "master": "jymaster",
    },
    'qualityMapReverse': {
        'standard': '128k',
        'exhigh': '320k',
        'lossless': 'flac',
        'hires': 'flac24bit',
        "jyeffect": "dolby",
        "jysky": "sky",
        "jymaster": "master",
    },
    'cookie': config.read_config('module.wy.user.cookie'),
}

async def url(songId, quality):
    path = '/api/song/enhance/player/url/v1'
    requestUrl = 'https://interface.music.163.com/eapi/song/enhance/player/url/v1'
    req = await Httpx.AsyncRequest(requestUrl, {
        'method': 'POST',
        'headers': {
            'Cookie': tools['cookie'],
        },
        'form': eapiEncrypt(path, json.dumps({
            "ids": json.dumps([songId]),
            "level": tools["qualityMap"][quality],
            "encodeType": "flac",
        }))
    })
    body = req.json()
    if (not body.get("data") or (not body.get("data")) or (not body.get("data")[0].get("url"))):
        raise FailedException("failed")

    data = body["data"][0]
    if (data['level'] != tools['qualityMap'][quality]):
        raise FailedException("reject unmatched quality")

    return {
        'url': data["url"].split("?")[0],
        'quality': tools['qualityMapReverse'][data['level']] 
    }

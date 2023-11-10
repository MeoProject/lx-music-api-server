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
        "jyeffect": "jyeffect",
        "jysky": "jysky",
        "jymaster": "jymaster",
    },
    'cookie': config.read_config('module.wy.user.cookie'),
}

async def url(songId, quality):
    path = '/api/song/enhance/player/url/v1'
    requestUrl = 'https://interface.music.163.com/eapi/song/enhance/player/url/v1'
    req = Httpx.request(requestUrl, {
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
    body = json.loads(req.text)
    if (not body.get("data") or (not body.get("data")) or (not body.get("data")[0].get("url"))):
        raise FailedException("failed")
    return body["data"][0]["url"].split("?")[0]

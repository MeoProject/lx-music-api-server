# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: player.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from common import config, utils, variable, Httpx
from .musicInfo import getMusicInfo
from .utils import tools
from .utils import signRequest
import random

createObject = utils.CreateObject

index_map = {
    'dolby': 4,
    'master': 3
}

async def vkeyUrl(q, b):
    apiNode = config.read_config("module.tx.vkey_api.vkey_api_url")
    filename = b['track_info']['file']['media_mid']
    if (q in index_map.keys()):
        filename = b['track_info']['vs'][index_map[q]]
    if (not filename): raise FailedException('未找到该音质')
    filename = f"{tools.fileInfo[q]['h']}{filename}{tools.fileInfo[q]['e']}"
    url = apiNode + f"?filename={filename}&guid={config.read_config('module.tx.vkeyserver.guid')}&uin={config.read_config('module.tx.vkeyserver.uin')}"
    req = await Httpx.AsyncRequest(url)
    body = req.json()
    purl = body['data'][0]['purl']
    
    return {
        'url': tools.cdnaddr + purl,
        'quality': q
    }

async def url(songId, quality):
    infoBody = await getMusicInfo(songId)
    strMediaMid = infoBody['track_info']['file']['media_mid']
    if (config.read_config("module.tx.vkey_api.use_vkey_api")):
        return await vkeyUrl(quality, infoBody)
    user_info = config.read_config('module.tx.user') if (not variable.use_cookie_pool) else random.choice(config.read_config('module.cookiepool.tx'))
    requestBody = {
        'req_0': {
            'module': 'vkey.GetVkeyServer',
            'method': 'CgiGetVkey',
            'param': {
                'filename': [f"{tools.fileInfo[quality]['h']}{strMediaMid}{tools.fileInfo[quality]['e']}"],
                'guid': config.read_config('module.tx.vkeyserver.guid'),
                'songmid': [songId],
                'songtype': [0],
                'uin': str(user_info['uin']),
                'loginflag': 1,
                'platform': '20',
            },
        },
        'comm': {
            "qq": str(user_info['uin']),
            "authst": user_info['qqmusic_key'],
            "ct": "26",
            "cv": "2010101",
            "v": "2010101"
        },
    }
    req = await signRequest(requestBody)
    body = createObject(req.json())
    data = body.req_0.data.midurlinfo[0]
    url = data['purl']

    if (not url):
        raise FailedException('failed')

    resultQuality = data['filename'].split('.')[0][:4]

    return {
        'url': tools.cdnaddr + url,
        'quality': tools.qualityMapReverse[resultQuality]
    }

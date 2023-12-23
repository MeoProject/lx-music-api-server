# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: player.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from common import config, utils
from .musicInfo import getMusicInfo
from .utils import tools
from .utils import signRequest

createObject = utils.CreateObject

async def url(songId, quality):
    infoBody = await getMusicInfo(songId)
    strMediaMid = infoBody['track_info']['file']['media_mid']
    requestBody = {
        'req_0': {
            'module': 'vkey.GetVkeyServer',
            'method': 'CgiGetVkey',
            'param': {
                'filename': [f"{tools.fileInfo[quality]['h']}{strMediaMid}{tools.fileInfo[quality]['e']}"],
                'guid': tools.guid,
                'songmid': [songId],
                'songtype': [0],
                'uin': tools.uin,
                'loginflag': 1,
                'platform': '20',
            },
        },
        'comm': {
            "qq": config.read_config('module.tx.user.uin'),
            "authst": config.read_config('module.tx.user.qqmusic_key'),
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

# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: utils.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from common import utils
from common import config
from .QMWSign import sign
import ujson as json

createObject = utils.CreateObject

tools = createObject({
    "fileInfo": {
        "128k": {
            'e': '.mp3',
            'h': 'M500',
        },
        '320k': {
            "e": '.mp3',
            'h': 'M800',
        },
        'flac': {
            "e": '.flac',
            'h': 'F000',
        },
        'flac24bit': {
            "e": '.flac',
            'h': 'RS01',
        },
        "dolby": {
            "e": ".flac",
            "h": "Q000",
        },
        "master": {
            "e": ".flac",
            "h": "AI00",
        }
    },
    'qualityMapReverse': {
        'M500': '128k',
        'M800': '320k',
        'F000': 'flac',
        'RS01': 'flac24bit',
        'Q000': 'dolby',
        'AI00': 'master'
    },
    "loginuin": config.read_config("module.tx.user.uin"),
    "guid": config.read_config("module.tx.vkeyserver.guid"),
    "cdnaddr": config.read_config("module.tx.cdnaddr") if config.read_config("module.tx.cdnaddr") else 'http://ws.stream.qqmusic.qq.com/',
})

async def signRequest(data, cache = False):
    data = json.dumps(data)
    s = sign(data)
    headers = {}
    return await Httpx.AsyncRequest('https://u.y.qq.com/cgi-bin/musics.fcg?format=json&sign=' + s, {
        'method': 'POST',
        'body': data,
        'headers': headers,
        "cache": (86400 * 30) if cache else "no-cache"
    })

def formatSinger(singerList):
    n = []
    for s in singerList:
        n.append(s['name'])
    return '、'.join(n)
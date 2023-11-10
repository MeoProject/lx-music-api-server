# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from common import Httpx
from common import utils
from common import config
from .QMWSign import sign
import ujson as json

jsobject = utils.jsobject

tools = jsobject({
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
    },
    "key": config.read_config("module.tx.user.qqmusic_key"),
    "loginuin": config.read_config("module.tx.user.uin"),
    "guid": config.read_config("module.tx.vkeyserver.guid"),
    "uin": config.read_config("module.tx.vkeyserver.uin"),
})


def signRequest(data):
    data = json.dumps(data)
    s = sign(data)
    headers = {}
    return Httpx.request('https://u.y.qq.com/cgi-bin/musics.fcg?format=json&sign=' + s, {
        'method': 'POST',
        'body': data,
        'headers': headers
    })


async def url(songId, quality):
    requestBody = {
        'req_0': {
            'module': 'vkey.GetVkeyServer',
            'method': 'CgiGetVkey',
            'param': {
                'filename': [f"{tools.fileInfo[quality]['h']}{songId}{tools.fileInfo[quality]['e']}"],
                'guid': tools.guid,
                'songmid': [songId],
                'songtype': [0],
                'uin': tools.uin,
                'loginflag': 1,
                'platform': '20',
            },
        },
        'comm': {
            "qq": tools.loginuin,
            "authst": tools.key,
            "ct": "26",
            "cv": "2010101",
            "v": "2010101"
        },
    }
    req = signRequest(requestBody)
    body = jsobject(req.json())
    # js const { purl } = data.req_0.data.midurlinfo[0]
    if (not body.req_0.data.midurlinfo[0]['purl']):
        raise FailedException('failed')
    return 'http://ws.stream.qqmusic.qq.com/' + body.req_0.data.midurlinfo[0]['purl']

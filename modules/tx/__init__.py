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
    "key": config.read_config("module.tx.user.qqmusic_key"),
    "loginuin": config.read_config("module.tx.user.uin"),
    "guid": config.read_config("module.tx.vkeyserver.guid"),
    "uin": config.read_config("module.tx.vkeyserver.uin"),
    "cdnaddr": config.read_config("module.tx.cdnaddr") if config.read_config("module.tx.cdnaddr") else 'http://ws.stream.qqmusic.qq.com/',
})


def signRequest(data, cache = False):
    data = json.dumps(data)
    s = sign(data)
    headers = {}
    return Httpx.request('https://u.y.qq.com/cgi-bin/musics.fcg?format=json&sign=' + s, {
        'method': 'POST',
        'body': data,
        'headers': headers,
        "cache": (86400 * 30) if cache else "no-cache"
    })


async def url(songId, quality):
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
                "song_mid": songId,
            },
        },
    }
    infoRequest = signRequest(infoReqBody, True)
    infoBody = createObject(infoRequest.json())
    if (infoBody.code != 0 or infoBody.req.code != 0):
        raise FailedException("获取音乐信息失败")
    strMediaMid = infoBody.req.data.track_info.file.media_mid
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
            "qq": tools.loginuin,
            "authst": tools.key,
            "ct": "26",
            "cv": "2010101",
            "v": "2010101"
        },
    }
    req = signRequest(requestBody)
    body = createObject(req.json())
    data = body.req_0.data.midurlinfo[0]
    url = data['purl']

    if (not url):
        raise FailedException('failed')

    try:
        resultQuality = data['filename'].split('.')[0].replace(data['songmid'], '')
    except:
        resultQuality = None

    return {
        'url': tools.cdnaddr + url,
        'quality': tools.qualityMapReverse[resultQuality]
    }


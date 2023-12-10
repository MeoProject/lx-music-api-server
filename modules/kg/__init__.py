# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from common import utils
from common import config
from common import Httpx
import ujson as json
import time

createObject = utils.CreateObject

def buildSignatureParams(dictionary, body = ""):
    joined_str = ''.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str + body

def buildRequestParams(dictionary):
    joined_str = '&'.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str

tools = createObject({
    "signkey": config.read_config("module.kg.client.signatureKey"),
    "pidversec": config.read_config("module.kg.client.pidversionsecret"),
    "clientver": config.read_config("module.kg.client.clientver"),
    "x-router": config.read_config("module.kg.tracker.x-router"),
    "url": config.read_config("module.kg.tracker.host") + config.read_config("module.kg.tracker.path"),
    "version": config.read_config("module.kg.tracker.version"),
    "userid": config.read_config("module.kg.user.userid"),
    "token": config.read_config("module.kg.user.token"),
    "mid": config.read_config("module.kg.user.mid"),
    "extra_params": config.read_config("module.kg.tracker.extra_params"),
    "appid": config.read_config("module.kg.client.appid"),
    'qualityHashMap': {
        '128k': 'hash_128',
        '320k': 'hash_320',
        'flac': 'hash_flac',
        'flac24bit': 'hash_high',
        'master': 'hash_128',
    },
    'qualityMap': {
        '128k': '128',
        '320k': '320',
        'flac': 'flac',
        'flac24bit': 'high',
        'master': 'viper_atmos',
    },
})

def sign(params, body = ""):
    params = utils.sortDict(params)
    params = buildSignatureParams(params, body)
    return utils.createMD5(tools["signkey"] + params + tools["signkey"])

def signRequest(url, params, options):
    params = utils.mergeDict(tools["extra_params"], params)
    url = url + "?" + buildRequestParams(params) + "&signature=" + sign(params, options.get("body") if options.get("body") else (options.get("data") if options.get("data") else ""))
    return Httpx.request(url, options)

def getKey(hash_):
    # print(hash_ + tools.pidversec + tools.appid + tools.mid + tools.userid)
    return utils.createMD5(hash_.lower() + tools.pidversec + tools.appid + tools.mid + tools.userid)

async def getMusicInfo(hash_):
    tn = int(time.time())
    url = "http://gateway.kugou.com/v3/album_audio/audio"
    options = {
        "method": "POST",
        "headers": {
            "KG-THash": "13a3164",
            "KG-RC": "1",
            "KG-Fake": "0",
            "KG-RF": "00869891",
            "User-Agent": "Android712-AndroidPhone-11451-376-0-FeeCacheUpdate-wifi",
            "x-router": "kmr.service.kugou.com",
        },
        "data": {
            "area_code": "1",
            "show_privilege": "1",
            "show_album_info": "1",
            "is_publish": "",
            "appid": 1005,
            "clientver": 11451,
            "mid": tools.mid,
            "dfid": "-",
            "clienttime": tn,
            "key": 'OIwlieks28dk2k092lksi2UIkp',
            "fields": "audio_info,album_info,album_audio_id",
            "data": [
                {
                    "hash": hash_
                }
            ]
        },
        'cache': 86400 * 15,
        'cache-ignore': [tn]
    }
    options['body'] = json.dumps(options['data']).replace(', ', ',').replace(': ', ':')
    return Httpx.request(url, dict(options)).json()['data'][0][0]

async def url(songId, quality):
    songId = songId.lower()
    body_ = await getMusicInfo(songId)
    thash = body_['audio_info'][tools.qualityHashMap[quality]]
    albumid = body_['album_info']['album_id'] if (body_.get('album_info') and body_['album_info'].get('album_id')) else None
    albumaudioid = body_['album_audio_id'] if (body_.get('album_audio_id')) else None
    if (not thash):
        raise FailedException('获取歌曲信息失败')
    if (not albumid):
        albumid = ""
    if (not albumaudioid):
        albumaudioid = ""
    thash = thash.lower()
    params = {
        'album_id': albumid,
        'userid': tools.userid,
        'area_code': 1,
        'hash': thash.lower(),
        'module': '',
        'mid': tools.mid,
        'appid': tools.appid,
        'ssa_flag': 'is_fromtrack',
        'clientver': tools.clientver,
        'open_time': time.strftime("%Y%m%d"),
        'vipType': 6,
        'ptype': 0,
        'token': tools.token,
        'auth': '',
        'mtype': 0,
        'album_audio_id': albumaudioid,
        'behavior': 'play',
        'clienttime': int(time.time()),
        'pid': 2,
        'key': getKey(thash),
        'dfid': '-',
        'pidversion': 3001
    }
    if (tools.version == 'v5'):
        params['quality'] = tools.qualityMap[quality]
        # print(params.quality)
    if (tools.version == "v4"):
        params['version'] = tools.clientver
    headers = createObject({
            'User-Agent': 'Android712-AndroidPhone-8983-18-0-NetMusic-wifi',
            'KG-THash': '3e5ec6b',
            'KG-Rec': '1',
            'KG-RC': '1',
        })
    if (tools['x-router']['enable']):
        headers['x-router'] = tools['x-router']['value']
    req = signRequest(tools.url, params, {'headers': headers})
    body = createObject(req.json())
    
    if body.status == 3:
        raise FailedException('该歌曲在酷狗没有版权，请换源播放')
    elif body.status == 2:
        raise FailedException('链接获取失败，请检查账号是否有会员或数字专辑是否购买')
    elif body.status != 1:
        raise FailedException('链接获取失败，可能是数字专辑或者api失效')
    return body.url[0]

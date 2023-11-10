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
import time

jsobject = utils.jsobject

def buildsignparams(dictionary, body = ""):
    joined_str = ''.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str + body

def buildrequestparams(dictionary):
    joined_str = '&'.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str

tools = jsobject({
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
        '128k': '128hash',
        '320k': '320hash',
        'flac': 'sqhash',
        'flac24bit': 'highhash',
    },
    'qualityMap': {
        '128k': '128',
        '320k': '320',
        'flac': 'flac',
        'flac24bit': 'high',
    },
})

def sign(params, body = ""):
    params = utils.sort_dict(params)
    params = buildsignparams(params, body)
    return utils.md5(tools["signkey"] + params + tools["signkey"])

def signRequest(url, params, options):
    params = utils.merge_dict(tools["extra_params"], params)
    url = url + "?" + buildrequestparams(params) + "&signature=" + sign(params, options.get("body") if options.get("body") else (options.get("data") if options.get("data") else ""))
    return Httpx.request(url, options)

def getKey(hash_):
    # print(hash_ + tools.pidversec + tools.appid + tools.mid + tools.userid)
    return utils.md5(hash_.lower() + tools.pidversec + tools.appid + tools.mid + tools.userid)

async def url(songId, quality):
    inforeq = Httpx.request("https://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash=" + songId)
    body_ = jsobject(inforeq.json())
    thash = body_.extra[tools.qualityHashMap[quality]]
    albumid = body_.albumid
    albumaudioid = body_.album_audio_id
    if (not thash):
        raise FailedException('获取歌曲信息失败')
    if (not albumid):
        albumid = 0
    if (not albumaudioid):
        albumaudioid = 0
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
    headers = jsobject({
            'User-Agent': 'Android712-AndroidPhone-8983-18-0-NetMusic-wifi',
            'KG-THash': '3e5ec6b',
            'KG-Rec': '1',
            'KG-RC': '1',
        })
    if (tools['x-router']['enable']):
        headers['x-router'] = tools['x-router']['value']
    req = signRequest(tools.url, params, {'headers': headers})
    body = jsobject(req.json())
    
    if body.status == 3:
        raise FailedException('该歌曲在酷狗没有版权，请换源播放')
    elif body.status == 2:
        raise FailedException('链接获取失败，请检查账号信息是否过期或本歌曲为数字专辑')
    elif body.status != 1:
        raise FailedException('链接获取失败，可能是数字专辑或者api失效')
    return body.url[0]

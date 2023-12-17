# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: musicInfo.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.utils import createMD5
from common import Httpx
from .utils import tools, signRequest
import random
import ujson as json
import time

async def getMusicInfo(hash_, use_cache = True):
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
            "key": 'OIlwlieks28dk2k092lksi2UIkp',
            "fields": "",
            "data": [
                {
                    "hash": hash_
                }
            ]
        },
        'cache': 86400 * 30 if use_cache else 'no-cache',
        'cache-ignore': [tn]
    }
    options['body'] = json.dumps(options['data']).replace(', ', ',').replace(': ', ':')
    body = await Httpx.AsyncRequest(url, dict(options))
    body = body.json()
    return body['data'][0][0] if (body['data'] and body['data'][0]) else {}

async def getMusicSingerInfo(hash_, use_cache = True):
    # https://expendablekmrcdn.kugou.com/container/v2/image?album_image_type=-3&appid=1005&author_image_type=4%2C5&clientver=12029&count=5&data=%5B%7B%22mixSongId%22%3A452960726%2C%22album_id%22%3A62936873%2C%22hash%22%3A%2241f45664e8235b786990cbf213cd4725%22%2C%22filename%22%3A%22%E8%A2%81%E5%B0%8F%E8%91%B3%E3%80%81%E9%98%BF%E8%BE%B0%EF%BC%88%E9%98%8E%E8%BE%B0%EF%BC%89%20-%20%E5%8C%96%E4%BD%9C%E7%83%9F%E7%81%AB%E4%B8%BA%E4%BD%A0%E5%9D%A0%E8%90%BD%22%2C%22album_audio_id%22%3A452960726%7D%5D&isCdn=1&publish_time=1&signature=b6670b9d81ca1a4e52e186c4db74c7f2
    url = "https://expendablekmrcdn.kugou.com/container/v2/image"
    params = {
        "album_image_type": -3,
        "appid": 1005,
        "author_image_type": "4,5",
        "clientver": 12029,
        "count": 5,
        "data": json.dumps([
            {
                "hash": hash_.lower()
            }
        ]),
        "isCdn": 1,
        "publish_time": 1
    }
    uuid = createMD5(str(random.randint(100000, 999999)) + '114514')
    req = await signRequest(url, params, {
        'method': 'GET',
        'headers': {
            'User-Agent': 'Android712-AndroidPhone-11451-18-0-Avatar-wifi',
            'KG-THash': '2a2624f',
            'KG-RC': '1',
            'KG-Fake': '0',
            'KG-RF': '0074c2c4',
            'appid': '1005',
            'clientver': '11451',
            'uuid': uuid,
        },
        'cache': 86400 * 30 if use_cache else 'no-cache',
        'cache-ignore': [uuid]
    }, 'OIlwieks28dk2k092lksi2UIkp')
    authors = req.json()['data'][0]['author']
    res = []
    for a in authors:
        res.append({
            'name': a['author_name'],
            'id': a['author_id'],
            'avatar': a['sizable_avatar'].format(size = 1080),
            'sizable_avatar': a['sizable_avatar'],
        })
    return res

async def getMusicMVHash(hash_, use_cache = True):
    req = await Httpx.AsyncRequest('http://mobilecdnbj.kugou.com/api/v3/song/info?hash=' + hash_, {
            'method': 'GET',
            'cache': 86400 * 30 if use_cache else 'no-cache',
        })
    body = req.json()
    return body['data']['mvhash'] if (body['data']) else ''
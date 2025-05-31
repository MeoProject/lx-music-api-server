from common.utils import createMD5
from common import request
from .utils import signRequest
import random
import ujson as json
import time


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
        "body": {
            "area_code": "1",
            "show_privilege": "1",
            "show_album_info": "1",
            "is_publish": "",
            "appid": 1005,
            "clientver": 11451,
            "mid": "114514",
            "dfid": "-",
            "clienttime": tn,
            "key": "OIlwlieks28dk2k092lksi2UIkp",
            "data": [{"hash": hash_}],
        },
    }
    body = await request.AsyncRequest(url, dict(options))
    body = body.json()
    return body["data"][0][0] if (body["data"] and body["data"][0]) else {}


async def getMusicSingerInfo(hash_):
    url = "https://expendablekmrcdn.kugou.com/container/v2/image"
    params = {
        "album_image_type": -3,
        "appid": 1005,
        "author_image_type": "4,5",
        "clientver": 12029,
        "count": 5,
        "data": json.dumps([{"hash": hash_.lower()}]),
        "isCdn": 1,
        "publish_time": 1,
    }
    uuid = createMD5(str(random.randint(100000, 999999)) + "114514")
    req = await signRequest(
        url,
        params,
        {
            "method": "GET",
            "headers": {
                "User-Agent": "Android712-AndroidPhone-11451-18-0-Avatar-wifi",
                "KG-THash": "2a2624f",
                "KG-RC": "1",
                "KG-Fake": "0",
                "KG-RF": "0074c2c4",
                "appid": "1005",
                "clientver": "11451",
                "uuid": uuid,
            },
        },
        "OIlwieks28dk2k092lksi2UIkp",
    )
    authors = req.json()["data"][0]["author"]
    res = []
    for a in authors:
        res.append(
            {
                "name": a["author_name"],
                "id": a["author_id"],
                "avatar": a["sizable_avatar"].format(size=1080),
                "sizable_avatar": a["sizable_avatar"],
            }
        )
    return res

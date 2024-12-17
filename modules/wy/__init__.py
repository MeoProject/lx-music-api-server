# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import random
from common import Httpx, variable
from common import config
from common.exceptions import FailedException
from .encrypt import eapiEncrypt
import ujson as json
from . import refresh_login

tools = {
    'qualityMap': {
        '128k': 'standard',
        "192k": "higher",
        '320k': 'exhigh',
        'flac': 'lossless',
        'flac24bit': 'hires',
        "dolby": "jyeffect",
        "sky": "sky",
        "master": "jymaster",
        "standard": "standard",
        "higher": "higher",
        "exhigh": "exhigh",
        "lossless": "lossless",
        "hires": "hires",
        "jyeffect": "jyeffect",
        "jymaster": "jymaster",
    },
    'qualityMapReverse': {
        'standard': '128k',
        "higher": "192k",
        'exhigh': '320k',
        'lossless': 'flac',
        'hires': 'flac24bit',
        "jyeffect": "dolby",
        "sky": "sky",
        "jymaster": "master",
    },
}

async def url(songId, quality):
    path = '/api/song/enhance/player/url/v1'
    requestUrl = 'https://interface.music.163.com/eapi/song/enhance/player/url/v1'
    requestBody = {
        "ids": json.dumps([songId]),
        "level": tools["qualityMap"][quality],
        "encodeType": "flac",
    }
    if (quality == "sky"):
        requestBody["immerseType"] = "c51"
    req = await Httpx.AsyncRequest(requestUrl, {
        'method': 'POST',
        'headers': {
            'Cookie': config.read_config('module.wy.user.cookie') if (not variable.use_cookie_pool) else random.choice(config.read_config('module.cookiepool.wy'))['cookie'],
        },
        'form': eapiEncrypt(path, json.dumps(requestBody))
    })


# 发 GET 请求给第三方 Netease Cloud Music API 服务器获取链接（多此一举）|| 其实是我个人莫名其妙拿不到 Hires 以上音质的一种无奈替代方案
# 想自建服务器？可以参考这份教程：https://github.com/kirakirai8023/NeteaseCloudMusicApi
# 总之，在我的测试环境下很神奇，这个版本的 /song/url/v1 接口才能获取到最高音质，最新版本的 NeteaseCloudMusicApi 也不行
# 我懒得抓包了，等有缘人来改吧，哈哈

'''
async def url(songId, quality):
    requestUrl = 'https://your-netease-api-server.com/song/url/v1'
    params = {
        "id": songId,
        "level": tools["qualityMap"][quality],
        "cookie": config.read_config('module.wy.user.cookie')
                    if not variable.use_cookie_pool
                    else random.choice(config.read_config('module.cookiepool.wy'))['cookie']
    }

    req = await Httpx.AsyncRequest(requestUrl, {
        'method': 'GET',
        'params': params,
    })
'''

    body = req.json()
    if (not body.get("data") or (not body.get("data")) or (not body.get("data")[0].get("url"))):
        raise FailedException("failed")

    data = body["data"][0]
    if (data['level'] != tools['qualityMap'][quality]):
        raise FailedException("reject unmatched quality")

    return {
        'url': data["url"].split("?")[0],
        'quality': tools['qualityMapReverse'][data['level']] 
    }

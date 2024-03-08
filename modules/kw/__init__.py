# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import random
from common import Httpx, config, variable
from common.exceptions import FailedException
from common.utils import CreateObject
from .encrypt import base64_encrypt

tools = {
    'qualityMap': {
        '128k': '128kmp3',
        '320k': '320kmp3',
        'flac': '2000kflac',
        'flac24bit': '4000kflac',
        '128kmp3': '128kmp3',
        '320kmp3': '320kmp3',
        "2000kflac": "2000kflac",
        "4000kflac": "4000kflac",
    },
    'qualityMapReverse': {
        128: '128k',
        320: '320k',
        2000: 'flac',
        4000: 'flac24bit',
    },
    'extMap': {
        '128k': 'mp3',
        '320k': 'mp3',
        'flac': 'flac',
        'flac24bit': 'flac',
    }
}

async def url(songId, quality):
    proto = config.read_config('module.kw.proto')
    if (proto == 'bd-api'):
        user_info = config.read_config('module.kw.user') if (not variable.use_cookie_pool) else random.choice(config.read_config('module.cookiepool.kw'))
        target_url = f'''https://bd-api.kuwo.cn/api/service/music/downloadInfo/{songId}?isMv=0&format={tools['extMap'][quality]}&br={tools['qualityMap'][quality]}&uid={user_info['uid']}&token={user_info['token']}'''
        req = await Httpx.AsyncRequest(target_url, {
            'method': 'GET',
            'headers': {
                'User-Agent': 'Dart/2.14 (dart:io)',
                'channel': 'qq',
                'plat': 'ar',
                'net': 'wifi',
                'ver': '3.1.2',
                'uid': user_info['uid'],
                'devId': user_info['device_id'],
            }
        })
        try:
            body = req.json()
            data = body['data']

            if (body['code'] != 200) or (int(data['audioInfo']['bitrate']) == 1):
                raise FailedException('failed')

            return {
                'url': data['url'].split('?')[0],
                'quality': tools['qualityMapReverse'][int(data['audioInfo']['bitrate'])]
            }
        except:
            raise FailedException('failed')
    elif (proto == 'kuwodes'):
        des_info = config.read_config('module.kw.des')
        params = des_info['params'].format(
            songId = songId,
            map_quality = tools['qualityMap'][quality],
            ext = tools['extMap'][quality],
            raw_quality = quality,
        )
        target_url = f'https://{des_info["host"]}/{des_info["path"]}?f={des_info["f"]}&' + ('q=' + base64_encrypt(params) if (des_info["need_encrypt"]) else params)
        req = await Httpx.AsyncRequest(target_url, {
            'method': 'GET',
            'headers': des_info['headers']
        })
        url = ''
        bitrate = 1
        if (des_info["response_type"] == 'json'):
            url = req.json()
            for p in des_info['url_json_path'].split('.'):
                url = url.get(p)
                if (url == None):
                    raise FailedException('failed')
            bitrate = req.json()
            for p in des_info['bitrate_json_path'].split('.'):
                bitrate = bitrate.get(p)
                if (bitrate == None):
                    raise FailedException('failed')
        elif (des_info['response_type'] == 'text'):
            body = req.text
            for l in body.split('\n'):
                l = l.strip()
                if (l.startswith('url=')):
                    url = l.split('=')[1]
                elif (l.startswith('bitrate=')):
                    bitrate = int(l.split('=')[1])
        else:
            raise FailedException('配置文件参数response_type填写错误或不支持')
        bitrate = int(bitrate)
        if (url == '' or bitrate == 1):
            raise FailedException('failed')
        if (not url.startswith('http')):
            raise FailedException('failed')
        return {
            'url': url.split('?')[0],
            'quality': tools['qualityMapReverse'][bitrate]
        }
    else:
        raise FailedException('配置文件参数proto填写错误或不支持')

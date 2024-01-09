# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from modules.kw.encrypt import base64_encrypt
from common.exceptions import FailedException

tools = {
    'qualityMap': {
        '128k': '128kmp3',
        '320k': '320kmp3',
        'flac': '2000kflac',
    },
    'qualityMapReverse': {
        '128': '128k',
        '320': '320k',
        '2000': 'flac',
    },
    'extMap': {
        '128k': 'mp3',
        '320k': 'mp3',
        'flac': 'flac',
    }
}


async def url(songId, quality):
    # 原来的方法现在需要附带uid、token以及对应的登录设备的devId
    # target_url = f'''https://bd-api.kuwo.cn/api/service/music/downloadInfo/{songId}?isMv=0&format={tools['extMap'][quality]}&br={tools['qualityMap'][quality]}&uid=&token='''
    # req = await Httpx.AsyncRequest(target_url, {
    #     'method': 'GET',
    #     'headers': {
    #         'User-Agent': 'okhttp/3.10.0',
    #         'channel': 'qq',
    #         'plat': 'ar',
    #         'net': 'wifi',
    #         'ver': '3.1.2',
    #         'uid': '',
    #         'devId': '0',
    #     }
    # })
    # try:
    #     body = req.json()
    #     data = body['data']
    #
    #     if (body['code'] != 200) or (data['audioInfo']['bitrate'] == 1):
    #         raise FailedException('failed')
    #
    #     return {
    #         'url': data['url'].split('?')[0],
    #         'quality': tools['qualityMapReverse'][data['audioInfo']['bitrate']]
    #     }
    # except:
    #     raise FailedException('failed')

    target_url = 'http://mobi.kuwo.cn/mobi.s?f=kuwo&q=' + base64_encrypt(
        f'''user=0&android_id=0&prod=kwplayer_ar_8.5.5.0&corp=kuwo&newver=3&vipver=8.5.5.0&source=kwplayer_ar_8.5.5.0_apk_keluze.apk&p2p=1&notrace=0&type=convert_url2&br={tools['qualityMap'][quality]}&format={tools['extMap'][quality]}&rid={songId}&priority=bitrate&loginUid=0&network=WIFI&loginSid=0&mode=down''')
    req = await Httpx.AsyncRequest(target_url, {
        'method': 'GET',
        'headers': {
            'User-Agent': 'okhttp/3.10.0'
        }
    })
    try:
        data = req.text
        if req.status != 200:
            raise FailedException('failed')
        return {
            'url': data[data.find("url=") + len("url="):data.find('?', data.find("url=") + len("url="))],
            'quality': tools['qualityMapReverse'][
                data[data.find("bitrate=") + len("bitrate="):data.find('\r\n', data.find("bitrate=") + len("bitrate="))]]
        }
    except Exception as e:
        raise FailedException(e)

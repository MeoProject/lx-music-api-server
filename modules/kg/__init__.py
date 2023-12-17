# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: __init__.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from .musicInfo import getMusicMVHash as _getMVHash
from .musicInfo import getMusicSingerInfo as _getInfo2
from .musicInfo import getMusicInfo as _getInfo
from .utils import tools
from .player import url
from .mv import getMvInfo as _getMvInfo
from .mv import getMvPlayURL as _getMvUrl
from common.exceptions import FailedException
from common import Httpx
from common import utils
import asyncio

async def info(hash_):
    tasks = []
    tasks.append(_getInfo(hash_))
    tasks.append(_getInfo2(hash_))
    tasks.append(_getMVHash(hash_))
    res = await asyncio.gather(*tasks)
    res1 = res[0]
    res2 = res[1]
    file_info = {}
    for k, v in tools['qualityHashMap'].items():
        if (res1['audio_info'][v] and k != 'master'):
            file_info[k] = {
                'hash': res1['audio_info'][v],
                'size': utils.sizeFormat(int(res1['audio_info'][v.replace('hash', 'filesize')])),
            }
    
    if (isinstance(res1, type(None))):
        raise FailedException('获取歌曲信息失败，请检查歌曲是否存在')

    return {
        'name': res1['songname'],
        'name_ori': res1['ori_audio_name'],
        'name_extra': res1['songname'].replace(res1['ori_audio_name'], '').strip(),
        'singer': res1['author_name'],
        'singer_list': res2,
        'format_length': utils.timeLengthFormat(int(res1['audio_info']['timelength']) / 1000),
        'length': int(res1['audio_info']['timelength']) / 1000,
        'hash': res1['audio_info']['hash'],
        'file_info': file_info,
        'songmid': res1['audio_id'],
        'album_id': res1['album_info']['album_id'],
        'album': res1['album_info']['album_name'],
        'bpm': int(res1['bpm']),
        'language': res1['language'],
        'cover': res1['album_info']['sizable_cover'].format(size = 1080),
        'sizable_cover': res1['album_info']['sizable_cover'],
        'publish_date': res1['publish_date'],
        'mvid': res[2],
        'genre': []
    }

async def mv(hash_):
    tasks = []
    tasks.append(_getMvInfo(hash_))
    tasks.append(_getMvUrl(hash_))
    res = await asyncio.gather(*tasks)
    res1 = res[0]
    res2 = res[1]
    res1['play_info'] = res2
    return res1
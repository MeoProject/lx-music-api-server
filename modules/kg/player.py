# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: player.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
from common.exceptions import FailedException
from common import utils
from .utils import getKey, signRequest, tools
from .musicInfo import getMusicInfo
import time

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
        'hash': thash,
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
    if (tools.version == "v4"):
        params['version'] = tools.clientver
    params = utils.mergeDict(tools["extra_params"], params)
    headers = {
            'User-Agent': 'Android712-AndroidPhone-8983-18-0-NetMusic-wifi',
            'KG-THash': '3e5ec6b',
            'KG-Rec': '1',
            'KG-RC': '1',
        }
    if (tools['x-router']['enable']):
        headers['x-router'] = tools['x-router']['value']
    req = await signRequest(tools.url, params, {'headers': headers})
    body = req.json()

    if body['status'] == 3:
        raise FailedException('该歌曲在酷狗没有版权，请换源播放')
    elif body['status'] == 2:
        raise FailedException('链接获取失败，请检查账号是否有会员或数字专辑是否购买')
    elif body['status'] != 1:
        raise FailedException('链接获取失败，可能是数字专辑或者api失效')

    return {
        'url': body["url"][0],
        'quality': quality
    }
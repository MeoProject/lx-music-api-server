# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: mv.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from common import utils
from common.exceptions import FailedException

async def getMvInfo(mvhash, use_cache = True):
    req = await Httpx.AsyncRequest(f'http://mobilecdnbj.kugou.com/api/v3/mv/detail?mvhash={mvhash}', {
        'method': 'GET',
        'cache': 86400 * 30 if use_cache else 'no-cache',
    })
    body = req.json()
    if (body['status'] != 1):
        raise FailedException('获取失败')
    if (not body['data']['info']):
        raise FailedException('mv不存在')
    singers = []
    for s in body['data']['info']['authors']:
        singers.append({
            'name': s['singername'],
            'id': s['singerid'],
            'avatar': s['singeravatar'].format(size=1080),
            'sizable_avatar': s['singeravatar'],
        })
    tags = []
    for t in body['data']['info']['tags']:
        tags.append(t['tag_name'])
    return {
        'name': body['data']['info']['filename'].replace(body['data']['info']['singername'] + ' - ', ''),
        'name_ori': body['data']['info']['videoname'],
        'name_extra': body['data']['info']['remark'],
        'filename': body['data']['info']['filename'],
        'intro': body['data']['info']['description'],
        'music_hash': body['data']['info']['audio_info']['hash'],
        'music_id': body['data']['info']['audio_info']['audio_id'],
        'format_length': utils.timeLengthFormat(body['data']['info']['mv_timelength'] / 1000),
        'length': body['data']['info']['mv_timelength'] / 1000,
        'hash': body['data']['info']['hash'],
        'vid': body['data']['info']['video_id'],
        'singer': body['data']['info']['singername'],
        'singer_list': singers,
        'tags': tags,
        'cover': body['data']['info']['imgurl'].format(size=1080),
        'sizable_cover': body['data']['info']['imgurl'],
    }

async def getMvPlayURL(mvhash):
    req = await Httpx.AsyncRequest(f'https://m.kugou.com/app/i/mv.php?cmd=100&hash={mvhash}&ismp3=1&ext=mp4', {
        'method': 'GET'
    })
    body = req.json()
    if (body['status'] != 1):
        return {}
    formatted = {}
    if (body['mvdata']['le']):
        formatted['270p'] = {
            'url': body['mvdata']['le']['downurl'],
            'hash': body['mvdata']['le']['hash'],
            'bitrate': body['mvdata']['le']['bitrate'],
            'format_size': utils.sizeFormat(body['mvdata']['le']['filesize']),
            'size': body['mvdata']['le']['filesize'],
        }
    if (body['mvdata']['sq']):
        formatted['720p'] = {
            'url': body['mvdata']['sq']['downurl'],
            'hash': body['mvdata']['sq']['hash'],
            'bitrate': body['mvdata']['sq']['bitrate'],
            'format_size': utils.sizeFormat(body['mvdata']['sq']['filesize']),
            'size': body['mvdata']['sq']['filesize'],
        }
    if (body['mvdata']['rq']):
        formatted['1080p'] = {
            'url': body['mvdata']['rq']['downurl'],
            'hash': body['mvdata']['rq']['hash'],
            'bitrate': body['mvdata']['rq']['bitrate'],
            'format_size': utils.sizeFormat(body['mvdata']['rq']['filesize']),
            'size': body['mvdata']['rq']['filesize'],
        }
    return formatted
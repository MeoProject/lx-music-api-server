# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from .player import url
from .musicInfo import getMusicInfo as _getInfo
from .utils import formatSinger
from .lyric import getLyric as _getLyric
from common import utils
from . import refresh_login


async def info(songid):
    req = await _getInfo(songid)
    singerList = []
    for s in req['track_info']['singer']:
        s.pop('uin')
        s.pop('title')
        singerList.append(s)
    file_info = {}
    if (req['track_info']['file']['size_128mp3'] != 0):
        file_info['128k'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_128mp3'])),
        }
    if (req['track_info']['file']['size_320mp3'] != 0):
        file_info['320k'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_320mp3'])),
        }
    if (req['track_info']['file']['size_flac'] != 0):
        file_info['flac'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_flac'])),
        }
    if (req['track_info']['file']['size_hires'] != 0):
        file_info['flac24bit'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_hires'])),
        }
    if (req['track_info']['file']['size_dolby'] != 0):
        file_info['dolby'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_dolby'])),
        }
    if (req['track_info']['file']['size_new'][0] != 0):
        file_info['master'] = {
            'size': utils.sizeFormat(int(req['track_info']['file']['size_new'][0])),
        }
    genres = []
    # fix: KeyError: 'genre'
    if (req.get('info') and req['info'].get('genre') and req['info']['genre'].get('content')):
        for g in req['info']['genre']['content']:
            genres.append(g['value'])
    return {
        'name': req['track_info']['title'] + ' ' + req['track_info']['subtitle'].strip(),
        'name_ori': req['track_info']['title'],
        'name_extra': req['track_info']['subtitle'].strip(),
        'singer': formatSinger(req['track_info']['singer']),
        'singer_list': singerList,
        'format_length': utils.timeLengthFormat(int(req['track_info']['interval'])),
        'length': int(req['track_info']['interval']),
        'media_mid': req['track_info']['file']['media_mid'],
        'file_info': file_info,
        'songmid': req['track_info']['mid'],
        'album_id': req['track_info']['album']['id'],
        'album_mid': req['track_info']['album']['mid'],
        'album': req['track_info']['album']['title'] + ' ' + req['track_info']['album']['subtitle'].strip(),
        'language': req['info']['lan']['content'][0]['value'],
        'cover': f'https://y.qq.com/music/photo_new/T002R800x800M000{req["track_info"]["album"]["pmid"]}.jpg',
        'sizable_cover': 'https://y.qq.com/music/photo_new/T002R{size}x{size}M000' + f'{req["track_info"]["album"]["pmid"]}.jpg',
        'publish_date': req['track_info']['time_public'],
        'mvid': req['track_info']['mv']['vid'],
        'genre': genres,
        'kmid': req['track_info']['ksong']['mid'],
        'kid': req['track_info']['ksong']['id'],
        'bpm': req['track_info']['bpm'],
    }

async def lyric(songId):
    return await _getLyric(songId)


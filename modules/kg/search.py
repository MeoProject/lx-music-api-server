# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: search.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from common import utils
from common.exceptions import FailedException
from .utils import buildRequestParams

def formatSubResult(l):
    res = []
    for songinfo in l:
        fileinfo = {}
        if (songinfo['FileSize'] != 0):
            fileinfo['128k'] = {
                'hash': songinfo['FileHash'],
                'size': utils.sizeFormat(songinfo['FileSize']),
            }
        if (songinfo['HQFileSize'] != 0):
            fileinfo['320k'] = {
                'hash': songinfo['HQFileHash'],
                'size': utils.sizeFormat(songinfo['HQFileSize']),
            }
        if (songinfo['SQFileSize'] != 0):
            fileinfo['flac'] = {
                'hash': songinfo['SQFileHash'],
                'size': utils.sizeFormat(songinfo['SQFileSize']),
            }
        if (songinfo['ResFileSize'] != 0):
            fileinfo['flac24bit'] = {
                'hash': songinfo['ResFileHash'],
                'size': utils.sizeFormat(songinfo['ResFileSize']),
            }

        res.append({
            'name': songinfo['SongName'],
            'name_ori': songinfo['OriSongName'],
            'name_extra': songinfo['SongName'].replace(songinfo['OriSongName'], ''),
            'singer': songinfo['SingerName'],
            'singer_list': [{'name': i['name'], 'id': i['id']} for i in songinfo['Singers']],
            'isoriginal': True if (songinfo['IsOriginal'] == 1) else False,
            'tag': songinfo.get('TagContent') if songinfo.get('TagContent') else '',
            'format_length': utils.timeLengthFormat(songinfo['Duration']),
            'length': songinfo['Duration'],
            'hash': songinfo['FileHash'],
            'file_info': fileinfo,
            'songmid': songinfo['Audioid'],
            'album_id': songinfo['AlbumID'],
            'album': songinfo['AlbumName'],
            'language': songinfo['trans_param'].get('language') if songinfo['trans_param'] else '',
            'cover': songinfo['Image'].format(size = 1080),
            'sizable_cover': songinfo['Image'],
            'mvid': songinfo['MvHash'],
        })
    return res

async def getSongSearchResult(query, page = 1, size = 20):
    page = int(page)
    size = int(size)
    req = await Httpx.AsyncRequest(utils.encodeURI(f'https://songsearch.kugou.com/song_search_v2?' + buildRequestParams({
        "keyword": query,
        "page": page,
        "pagesize": size,
        "userid": 0,
        "clientver": "",
        "platform": "WebFilter",
        "filter": 2,
        "iscorrection": 1,
        "privilege_filter": 0
    })), {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36",
            "Referer": "https://www.kugou.com",
        }
    })
    body = req.json()
    if (body['status'] != 1):
        raise FailedException('歌曲搜索失败')
    if (body['data']['total'] == 0 or body['data']['lists'] == []):
        return {
            'total': 0,
            'page': page,
            'size': size,
            'list': [],
        }
    res = []
    for songinfo in body['data']['lists']:
        fileinfo = {}
        if (songinfo['FileSize'] != 0):
            fileinfo['128k'] = {
                'hash': songinfo['FileHash'],
                'size': utils.sizeFormat(songinfo['FileSize']),
            }
        if (songinfo['HQFileSize'] != 0):
            fileinfo['320k'] = {
                'hash': songinfo['HQFileHash'],
                'size': utils.sizeFormat(songinfo['HQFileSize']),
            }
        if (songinfo['SQFileSize'] != 0):
            fileinfo['flac'] = {
                'hash': songinfo['SQFileHash'],
                'size': utils.sizeFormat(songinfo['SQFileSize']),
            }
        if (songinfo['ResFileSize'] != 0):
            fileinfo['flac24bit'] = {
                'hash': songinfo['ResFileHash'],
                'size': utils.sizeFormat(songinfo['ResFileSize']),
            }

        res.append({
            'name': songinfo['SongName'],
            'name_ori': songinfo['OriSongName'],
            'name_extra': songinfo['SongName'].replace(songinfo['OriSongName'], ''),
            'singer': songinfo['SingerName'],
            'singer_list': [{'name': i['name'], 'id': i['id']} for i in songinfo['Singers']],
            'isoriginal': True if (songinfo['IsOriginal'] == 1) else False,
            'tag': songinfo.get('TagContent') if songinfo.get('TagContent') else '',
            'format_length': utils.timeLengthFormat(songinfo['Duration']),
            'length': songinfo['Duration'],
            'hash': songinfo['FileHash'],
            'file_info': fileinfo,
            'songmid': songinfo['Audioid'],
            'album_id': songinfo['AlbumID'],
            'album': songinfo['AlbumName'],
            'language': songinfo['trans_param'].get('language') if songinfo['trans_param'] else '',
            'cover': songinfo['Image'].format(size = 1080),
            'sizable_cover': songinfo['Image'],
            'mvid': songinfo['MvHash'],
            'subresult': [] if (songinfo['Grp'] == []) else formatSubResult(songinfo['Grp']),
        })
    return {
        'total': body['data']['total'],
        'page': page,
        'size': size,
        'list': res,
    }
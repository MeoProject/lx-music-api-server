# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from common.utils import require
from common import log
from common import config
# 从.引入的包并没有在代码中直接使用，但是是用require在请求时进行引入的，不要动
from . import kw
from . import mg
from . import kg
from . import tx
from . import wy
import traceback
import time

logger = log.log('api_handler')

sourceExpirationTime = {
    'tx': {
        "expire": True,
        "time": 80400,  # 不知道tx为什么要取一个这么不对劲的数字当过期时长
    },
    'kg': {
        "expire": True,
        "time": 24 * 60 * 60,  # 24 hours
    },
    'kw': {
        "expire": True,
        "time": 60 * 60  # 60 minutes
    },
    'wy': {
        "expire": True,
        "time": 20 * 60,  # 20 minutes
    },
    'mg': {
        "expire": False,
        "time": 0,
    }

}


async def url(source, songId, quality, query = {}):
    if (not quality):
        return {
            'code': 2,
            'msg': '需要参数"quality"',
            'data': None,
        }
    
    if (source == "kg"):
        songId = songId.lower()
    
    try:
        cache = config.getCache('urls', f'{source}_{songId}_{quality}')
        if cache:
            logger.debug(f'使用缓存的{source}_{songId}_{quality}数据，URL：{cache["url"]}')
            return {
                'code': 0,
                'msg': 'success',
                'data': cache['url'],
                'extra': {
                    'cache': True,
                    'quality': {
                        'target': quality,
                        'result': quality,
                    },
                    'expire': {
                        # 在更新缓存的时候把有效期的75%作为链接可用时长，现在加回来
                        'time': int(cache['time'] + (sourceExpirationTime[source]['time'] * 0.25)) if cache['expire'] else None,
                        'canExpire': cache['expire'],
                    }
                },
            }
    except:
        logger.error(traceback.format_exc())
    try:
        func = require('modules.' + source + '.url')
    except:
        return {
            'code': 1,
            'msg': '未知的源或不支持的方法',
            'data': None,
        }
    try:
        result = await func(songId, quality)
        logger.info(f'获取{source}_{songId}_{quality}成功，URL：{result["url"]}')

        canExpire = sourceExpirationTime[source]['expire']
        expireTime = sourceExpirationTime[source]['time'] + int(time.time())
        config.updateCache('urls', f'{source}_{songId}_{quality}', {
            "expire": canExpire,
            # 取有效期的75%作为链接可用时长
            "time": int(expireTime - sourceExpirationTime[source]['time'] * 0.25),
            "url": result['url'],
            })
        logger.debug(f'缓存已更新：{source}_{songId}_{quality}, URL：{result["url"]}, expire: {expireTime}')

        return {
            'code': 0,
            'msg': 'success',
            'data': result['url'],
            'extra': {
                'cache': False,
                'quality': {
                    'target': quality,
                    'result': result['quality'],
                },
                'expire': {
                    'time': expireTime if canExpire else None,
                    'canExpire': canExpire,
                },
            },
        }
    except FailedException as e:
        logger.info(f'获取{source}_{songId}_{quality}失败，原因：' + e.args[0])
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }

async def lyric(source, songId, _, query):
    cache = config.getCache('lyric', f'{source}_{songId}')
    if cache:
        return {
            'code': 0,
            'msg': 'success',
            'data': cache['data']
        }
    try:
        func = require('modules.' + source + '.lyric')
    except:
        return {
            'code': 1,
            'msg': '未知的源或不支持的方法',
            'data': None,
        }
    try:
        result = await func(songId)
        config.updateCache('lyric', f'{source}_{songId}', {
            "data": result,
            "time": int(time.time() + (86400 * 3)), # 歌词缓存3天
            "expire": True,
        })
        logger.debug(f'缓存已更新：{source}_{songId}, lyric: {result}')
        return {
            'code': 0,
            'msg': 'success',
            'data': result
        }
    except FailedException as e:
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }

async def search(source, songid, _, query):
    try:
        func = require('modules.' + source + '.search')
    except:
        return {
            'code': 1,
            'msg': '未知的源或不支持的方法',
            'data': None,
        }
    try:
        result = await func(songid, query)
        return {
            'code': 0,
            'msg': 'success',
            'data': result
        }
    except FailedException as e:
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }

async def other(method, source, songid, _, query):
    try:
        func = require('modules.' + source + '.' + method)
    except:
        return {
            'code': 1,
            'msg': '未知的源或不支持的方法',
            'data': None,
        }
    try:
        result = await func(songid)
        return {
            'code': 0,
            'msg': 'success',
            'data': result
        }
    except FailedException as e:
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }

async def info_with_query(source, songid, _, query):
    return await other('info', source, songid, None)
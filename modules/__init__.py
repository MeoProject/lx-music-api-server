# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you konw what you are doing.

from common.exceptions import FailedException
from common.utils import require
from common import log
from common import config
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
        "time": 15 * 60 * 60,  # 15 hours
    },
    'kg': {
        "expire": True,
        "time": 15 * 60 * 60,  # 15 hours
    },
    'kw': {
        "expire": True,
        "time": 30 * 60  # 30 minutes
    },
    'wy': {
        "expire": True,
        "time": 10 * 60,  # 10 minutes
    },
    'mg': {
        # no expiration
        "expire": False,
        "time": 0,
    }

}


async def handleApiRequest(command, source, songId, quality):
    try:
        cache = config.getCache('urls', f'{source}_{songId}_{quality}')
        if cache:
            logger.debug(f'使用缓存的{source}_{songId}_{quality}数据，URL：{cache["url"]}')
            return {
                'code': 0,
                'msg': 'success',
                'data': {
                    'url': cache['url'],
                    'cache': True,
                    'quality': {
                        'target': quality,
                        'result': quality,
                    }
                },
            }
    except:
        logger.error(traceback.format_exc())
    try:
        func = require('modules.' + source + '.' + command)
    except:
        return {
            'code': 1,
            'msg': '未知的源或命令',
            'data': None,
        }
    try:
        result = await func(songId, quality)
        logger.debug(f'获取{source}_{songId}_{quality}成功，URL：{result['url']}')

        canExpire = sourceExpirationTime[source]['expire']
        expireTime = sourceExpirationTime[source]['time'] + int(time.time())
        config.updateCache('urls', f'{source}_{songId}_{quality}', {
            "expire": canExpire,
            "time": expireTime,
            "url": result['url'],
            })
        logger.debug(f'缓存已更新：{source}_{songId}_{quality}, URL：{result['url']}, expire: {expireTime}')

        return {
            'code': 0,
            'msg': 'success',
            'data': {
                'url': result['url'],
                'cache': False,
                'quality': {
                    'target': quality,
                    'result': result['quality'],
                },
                'expire': {
                    'time': expireTime,
                    'canExpire': canExpire,
                },
            },
        }
    except FailedException as e:
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }
